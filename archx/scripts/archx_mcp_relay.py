"""Relays the plugin's stdio MCP session to the running ArchX app.

Codex and Claude start this process for the plugin (scripts/archx-mcp on macOS, scripts/archx-mcp.cmd on Windows). ArchX
itself serves the tools on a private local endpoint (src/desktop/plugin-mcp.ts): a socket in its data folder on macOS, a
named pipe on Windows. The relay passes the newline-delimited JSON-RPC messages in both directions and starts ArchX in the
background when it is not running yet. It runs with the Python that ArchX bundles, so the plugin needs nothing else installed.

The relay holds a connection to ArchX only while the host uses it. Every Codex thread and every Claude session starts its
own relay and keeps it for as long as it lives, but ArchX serves a limited number of connections at once (23.10.2026 on Tim's
Mac: 10 Codex threads and 6 Claude sessions held all 16, and the 17th session got no tools). After IDLE_SECONDS without an
open request the relay closes its connection; the next message opens a new one and repeats the host's initialize handshake
first, so the host never notices. The same reconnect carries a session across an ArchX restart.

Environment: ARCHX_APP (the ArchX app to start: the .app bundle on macOS, ArchiGPT.exe on Windows), ARCHX_DATA_DIRECTORY
(the app's data folder; set only for development profiles), ARCHX_NO_LAUNCH=1 (never start the app, only connect),
ARCHX_IDLE_SECONDS (how long an unused connection stays open; tests shorten it).
"""
import hashlib
import json
import os
import socket
import subprocess
import sys
import threading
import time
from typing import NoReturn, Optional, Union

START_TIMEOUT_S = 90.0
ANSWER_TIMEOUT_S = 30.0
IDLE_SECONDS = float(os.environ.get("ARCHX_IDLE_SECONDS") or 30)
# A starting ArchX closes connections until it can read the office's market (plugin-mcp.ts, pluginServes); a full app
# closes the newest one. Both end the connection before the first answer, so the relay tries again a few times.
REFUSED_RETRIES = 4
WINDOWS = sys.platform == "win32"
PLUGIN_START_SWITCH = "--archx-plugin-start"

NOT_RUNNING = "ArchX läuft nicht (keine Verbindung unter {endpoint})."
NOT_REACHABLE = ("ArchX wurde gestartet, ist aber nicht erreichbar. Öffnen Sie ArchX einmal von Hand und melden Sie sich an; "
                 "ältere Versionen ohne Plugin-Anschluss bitte aktualisieren.")
NO_APP = "Keine installierte ArchX-App gefunden. Installieren Sie ArchX von architekten.frontierx.ch."
REFUSED = ("ArchX hat die Verbindung abgelehnt. Das ArchX-Plugin steht Büros in der Schweiz und in Deutschland zur Verfügung; "
           "prüfen Sie in ArchX unter Einstellungen das Land des Büros.")
ENDED = "ArchX wurde während des Aufrufs beendet. Bitte den Auftrag noch einmal geben."

if WINDOWS:
    import _winapi


def log(message: str) -> None:
    sys.stderr.write(f"ArchX: {message}\n")
    sys.stderr.flush()


def fail(message: str) -> NoReturn:
    log(message)
    sys.exit(1)


def die(message: str) -> NoReturn:
    """Ends the relay from any thread; reader threads may still hold the standard streams, so no interpreter shutdown."""
    log(message)
    os._exit(1)


def data_directory() -> str:
    configured = os.environ.get("ARCHX_DATA_DIRECTORY")
    if configured:
        return configured
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ArchiGPT")
    if WINDOWS and os.environ.get("APPDATA"):
        return os.path.join(os.environ["APPDATA"], "ArchiGPT")
    fail("Das ArchX-Plugin läuft unter macOS und Windows.")


def endpoint_of(directory: str, windows: bool = WINDOWS) -> str:
    """Where ArchX listens; the same rule as pluginEndpoint in src/desktop/plugin-mcp.ts."""
    if windows:
        return r"\\.\pipe\archx-mcp-" + hashlib.sha256(directory.lower().encode("utf-8")).hexdigest()[:24]
    return os.path.join(directory, "plugin", "mcp.sock")


class SocketChannel:
    """One connection to ArchX over its Unix socket (macOS)."""

    def __init__(self, client: socket.socket) -> None:
        self._client = client

    def read(self) -> bytes:
        try:
            return self._client.recv(65536)
        except OSError:
            return b""

    def write(self, data: bytes) -> None:
        self._client.sendall(data)

    def shutdown(self) -> None:
        try:
            self._client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def release(self) -> None:
        self._client.close()


class PipeChannel:
    """One connection to ArchX over its named pipe (Windows). Overlapped I/O, because on a pipe opened for synchronous
    I/O Windows queues a write behind the pending read, and the read waits for ArchX's answer to that very write."""

    def __init__(self, handle: int) -> None:
        self._handle = handle
        self._reading = None
        self._closed = False

    def read(self) -> bytes:
        if self._closed:
            return b""
        try:
            overlapped, _ = _winapi.ReadFile(self._handle, 65536, overlapped=True)
            self._reading = overlapped
            if self._closed:  # shutdown() ran between ReadFile and the line above and saw no read to cancel
                self._cancel(overlapped)
            _, error = overlapped.GetOverlappedResult(True)
        except OSError:
            return b""
        finally:
            self._reading = None
        return b"" if error else bytes(overlapped.getbuffer())

    def write(self, data: bytes) -> None:
        overlapped, _ = _winapi.WriteFile(self._handle, data, overlapped=True)
        written, error = overlapped.GetOverlappedResult(True)
        if error or written != len(data):
            raise OSError(error, "ArchX pipe write incomplete")

    def shutdown(self) -> None:
        self._closed = True
        reading = self._reading
        if reading is not None:
            self._cancel(reading)

    @staticmethod
    def _cancel(overlapped) -> None:
        try:
            overlapped.cancel()
        except OSError:
            pass  # Already complete.

    def release(self) -> None:
        _winapi.CloseHandle(self._handle)


Channel = Union[SocketChannel, PipeChannel]


def connect(endpoint: str) -> Optional[Channel]:
    if not WINDOWS:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(endpoint)
            return SocketChannel(client)
        except OSError:
            client.close()
            return None
    deadline = time.monotonic() + 5
    while True:
        try:
            return PipeChannel(_winapi.CreateFile(endpoint, _winapi.GENERIC_READ | _winapi.GENERIC_WRITE, 0, _winapi.NULL,
                                                  _winapi.OPEN_EXISTING, _winapi.FILE_FLAG_OVERLAPPED, _winapi.NULL))
        except OSError as error:
            # Every pipe instance busy: ArchX is accepting another connection right now.
            if getattr(error, "winerror", None) != _winapi.ERROR_PIPE_BUSY or time.monotonic() > deadline:
                return None
            try:
                _winapi.WaitNamedPipe(endpoint, 1000)
            except OSError:
                pass


def launch_app() -> None:
    app = os.environ.get("ARCHX_APP")
    if not app:
        raise LookupError(NO_APP)
    if not WINDOWS:
        # -g -j: in the background and hidden, so a Codex or Claude session never puts the ArchX window on the screen.
        subprocess.run(["/usr/bin/open", "-g", "-j", "-a", app], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    # The switch keeps the window closed (src/desktop/hidden-start.ts). ArchX must outlive this relay: outside the host's job
    # object where the job allows it, and never with the host's console.
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    for extra in (subprocess.CREATE_BREAKAWAY_FROM_JOB, 0):
        try:
            subprocess.Popen([app, PLUGIN_START_SWITCH], creationflags=flags | extra, close_fds=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue
    raise LookupError(NO_APP)


def id_key(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def refusal(opened: Union[dict, str]) -> Optional[str]:
    """Why an opened connection cannot take requests, or None when it can."""
    if isinstance(opened, str):
        return opened
    error = opened.get("error")
    if error is None:
        return None
    return str(error.get("message")) if isinstance(error, dict) and error.get("message") else REFUSED


class Relay:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self._state = threading.Lock()  # channel, pending, waiting
        self._busy = threading.Lock()  # held while a host message is handled; the idle closer never interrupts that
        self._out = threading.Lock()
        self._channel: Optional[Channel] = None
        self._pending: dict = {}
        self._waiting: dict = {}  # relay's own initialize id -> [event, answer]
        self._serial = 0
        self._initialize_params: Optional[dict] = None
        self._initialized: Optional[bytes] = None
        self._last_use = time.monotonic()

    # Host side ---------------------------------------------------------------------------------------------------------

    def emit(self, message: dict) -> None:
        line = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        with self._out:
            try:
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
            except (OSError, ValueError):
                os._exit(0)  # The host is gone.

    def answer_error(self, request_id: object, message: str) -> None:
        self.emit({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": message}})

    def handle(self, line: bytes) -> None:
        try:
            message = json.loads(line)
        except ValueError:
            message = None
        if not isinstance(message, dict):
            self.forward(line, open_if_closed=True)
            return
        method, request_id = message.get("method"), message.get("id")
        self._last_use = time.monotonic()
        if isinstance(method, str) and request_id is not None:
            if method == "initialize":
                self.initialize(request_id, message.get("params") if isinstance(message.get("params"), dict) else {})
                return
            self.request(request_id, line)
        elif method == "notifications/initialized":
            self._initialized = line
            self.forward(line, open_if_closed=False)
        else:
            # Cancellations and other notifications only matter to an open connection; ArchX sends no requests to answer.
            self.forward(line, open_if_closed=False)

    def initialize(self, request_id: object, params: dict) -> None:
        self._initialize_params = params
        with self._state:
            channel = self._channel
        if channel is not None:
            self.drop(channel)
        result = self.open()
        if isinstance(result, str):
            self.answer_error(request_id, result)
            die(result)  # A host that cannot initialize shows this text as the plugin's start error.
        self.emit({**result, "id": request_id})

    def request(self, request_id: object, line: bytes) -> None:
        for _ in range(2):
            with self._state:
                channel = self._channel
            if channel is None:
                problem = refusal(self.open())
                if problem is not None:
                    self.answer_error(request_id, problem)
                    return
                with self._state:
                    channel = self._channel
                if channel is None:
                    continue
            with self._state:
                self._pending[id_key(request_id)] = request_id
            try:
                channel.write(line)
                return
            except OSError:
                with self._state:
                    self._pending.pop(id_key(request_id), None)
                self.drop(channel)
        self.answer_error(request_id, NOT_REACHABLE)

    def forward(self, line: bytes, open_if_closed: bool) -> None:
        with self._state:
            channel = self._channel
        if channel is None and open_if_closed and refusal(self.open()) is None:
            with self._state:
                channel = self._channel
        if channel is None:
            return
        try:
            channel.write(line)
        except OSError:
            self.drop(channel)

    # ArchX side --------------------------------------------------------------------------------------------------------

    def open(self) -> Union[dict, str]:
        """Opens a connection and repeats the host's initialize on it; the initialize answer, or why there is none."""
        for attempt in range(REFUSED_RETRIES + 1):
            channel = connect(self.endpoint)
            if channel is None:
                if os.environ.get("ARCHX_NO_LAUNCH") == "1":
                    return NOT_RUNNING.format(endpoint=self.endpoint)
                try:
                    launch_app()
                except LookupError as error:
                    return str(error)
                deadline = time.monotonic() + START_TIMEOUT_S
                while channel is None and time.monotonic() < deadline:
                    time.sleep(0.25)
                    channel = connect(self.endpoint)
                if channel is None:
                    return NOT_REACHABLE
            with self._state:
                self._channel = channel
            threading.Thread(target=self.pump, args=(channel,), daemon=True).start()
            if self._initialize_params is None:
                return {}
            answer = self.handshake(channel)
            if answer is not None:
                if "error" in answer:
                    self.drop(channel)
                return answer
            self.drop(channel)
            time.sleep(min(0.5 * (attempt + 1), 2.0))
        return REFUSED

    def handshake(self, channel: Channel) -> Optional[dict]:
        self._serial += 1
        own_id = f"archx-relay-{self._serial}"
        slot = [threading.Event(), None]
        with self._state:
            self._waiting[own_id] = slot
        request = {"jsonrpc": "2.0", "id": own_id, "method": "initialize", "params": self._initialize_params}
        try:
            channel.write(json.dumps(request, ensure_ascii=False).encode("utf-8") + b"\n")
            slot[0].wait(ANSWER_TIMEOUT_S)
        except OSError:
            pass
        finally:
            with self._state:
                self._waiting.pop(own_id, None)
        answer = slot[1]
        if answer is not None and "error" not in answer and self._initialized is not None:
            try:
                channel.write(self._initialized)
            except OSError:
                return None
        return answer

    def pump(self, channel: Channel) -> None:
        buffer = b""
        try:
            while True:
                chunk = channel.read()
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        self.from_app(line)
        finally:
            self.ended(channel)
            channel.release()

    def from_app(self, line: bytes) -> None:
        self._last_use = time.monotonic()
        try:
            message = json.loads(line)
        except ValueError:
            message = None
        if isinstance(message, dict) and "method" not in message and "id" in message:
            with self._state:
                slot = self._waiting.get(message["id"]) if isinstance(message["id"], str) else None
                if slot is None:
                    self._pending.pop(id_key(message["id"]), None)
            if slot is not None:
                slot[1] = message
                slot[0].set()
                return
        with self._out:
            try:
                sys.stdout.buffer.write(line + b"\n")
                sys.stdout.buffer.flush()
            except (OSError, ValueError):
                os._exit(0)

    def ended(self, channel: Channel) -> None:
        with self._state:
            current = self._channel is channel
            if current:
                self._channel = None
            lost = list(self._pending.values()) if current else []
            if current:
                self._pending.clear()
                # Only the open connection's handshake waits here; a connection that was already let go (idle, refused)
                # and ends late must not wake the handshake on its successor.
                for slot in self._waiting.values():
                    slot[0].set()
        for request_id in lost:
            self.answer_error(request_id, ENDED)

    def drop(self, channel: Channel) -> None:
        with self._state:
            if self._channel is channel:
                self._channel = None
        channel.shutdown()

    def close_when_idle(self) -> None:
        while True:
            time.sleep(min(1.0, IDLE_SECONDS / 4))
            if not self._busy.acquire(blocking=False):
                continue
            try:
                with self._state:
                    channel = self._channel
                    idle = channel is not None and not self._pending and time.monotonic() - self._last_use >= IDLE_SECONDS
                    if idle:
                        self._channel = None
                if idle:
                    channel.shutdown()
            finally:
                self._busy.release()


def main() -> None:
    relay = Relay(endpoint_of(data_directory()))
    threading.Thread(target=relay.close_when_idle, daemon=True).start()
    stdin = sys.stdin.buffer
    while True:
        line = stdin.readline()
        if not line:
            break
        if not line.strip():
            continue
        with relay._busy:
            relay.handle(line.rstrip(b"\r\n") + b"\n")
    with relay._state:
        channel = relay._channel
    if channel is not None:
        channel.shutdown()
    with relay._out:
        sys.stdout.flush()
    os._exit(0)  # Reader threads may still wait on ArchX; nothing they could deliver has a reader any more.


if __name__ == "__main__":
    main()
