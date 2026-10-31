@echo off
rem Starts the English ArchX plugin's MCP connection on Windows: finds the installed ArchX app and relays to it with the Python
rem ArchX bundles, with the relay's messages in English. Codex and Claude find this file for scripts/archx-mcp through PATHEXT, so
rem one manifest serves macOS and Windows. No parenthesised blocks: a user folder like "C:\Users\Name (Office)" would end them early.
setlocal EnableExtensions DisableDelayedExpansion
set "ARCHX_PLUGIN_LANGUAGE=en"
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
>&2 echo ArchX: No installed ArchX app found. Install ArchX from architekten.frontierx.ch.
exit /b 1

:no_python
>&2 echo ArchX: The Python runtime is missing from the ArchX installation in "%ARCHX_HOME%". Install ArchX again from architekten.frontierx.ch.
exit /b 1
