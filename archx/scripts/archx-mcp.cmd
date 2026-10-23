@echo off
rem Starts the ArchX plugin's MCP connection on Windows: finds the installed ArchX app and relays to it with the Python
rem ArchX bundles. Codex and Claude find this file for scripts/archx-mcp through PATHEXT, so one manifest serves macOS and
rem Windows. No parenthesised blocks: a user folder like "C:\Users\Name (Buero)" would end them early.
setlocal EnableExtensions DisableDelayedExpansion
if not defined ARCHX_APP set "ARCHX_APP=%LOCALAPPDATA%\ArchiGPT\ArchiGPT.exe"
if not exist "%ARCHX_APP%" goto no_app
for %%I in ("%ARCHX_APP%") do set "ARCHX_HOME=%%~dpI"
set "ARCHX_PYTHON="
rem Squirrel keeps the current and the previous version side by side; the last folder in name order wins. Name
rem order is not version order (app-0.0.99 after app-0.0.100), but the Python of either version runs the relay.
for /d %%D in ("%ARCHX_HOME%app-*") do if exist "%%~fD\resources\document-runtime\python\python.exe" set "ARCHX_PYTHON=%%~fD\resources\document-runtime\python\python.exe"
if not defined ARCHX_PYTHON goto no_python
"%ARCHX_PYTHON%" -I -B -X utf8 "%~dp0archx_mcp_relay.py"
exit /b %ERRORLEVEL%

:no_app
>&2 echo ArchX: Keine installierte ArchX-App gefunden. Installieren Sie ArchX von architekten.frontierx.ch.
exit /b 1

:no_python
>&2 echo ArchX: In der ArchX-Installation unter "%ARCHX_HOME%" fehlt die Python-Laufzeit. Installieren Sie ArchX neu von architekten.frontierx.ch.
exit /b 1
