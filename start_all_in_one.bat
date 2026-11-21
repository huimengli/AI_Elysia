@echo off
rem ============================================================
rem  start_all_in_one.bat - single-window launcher (design v3.1 section 8)
rem  ONE window only: jarvis. jarvis is the PARENT of llama-server (:8080)
rem  and GPT-SoVITS api_v2 (:9880), so their stdout lands in jarvis pipes
rem  and the /monitor page shows them (start_all.bat cannot do this: its
rem  "start cmd /k" windows own their own stdout).
rem  Closing this window kills ONLY the pids jarvis recorded in
rem  .tmp\jarvis_child_pids.json; services started elsewhere are left alone.
rem  start_all.bat is kept byte-identical (4 windows, status panel included).
rem  ASCII only, CRLF (self-report 52: I once wrote Chinese bytes into a bat
rem  with latin1 and the window printed a syntax-error message.)
rem  with latin1 and the window printed a syntax-error message.)
setlocal
cd /d %~dp0

rem ---- writable matplotlib cache (kills the WinError 5 AppData\Local\matplotlib warning) ----
set "MPLCONFIGDIR=%~dp0.tmp\mplconfig"
if not exist "%~dp0.tmp\mplconfig" mkdir "%~dp0.tmp\mplconfig"

rem ---- env: same as start_all.bat (HB-029: HF_ENDPOINT must carry the scheme) ----
set "HF_ENDPOINT=https://hf-mirror.com"
set "HF_HOME=%~dp0.hf-cache"
set "HF_HUB_DISABLE_XET=1"
set "JARVIS_ONE_WINDOW=1"

rem jarvis launches llama-server and api_v2 itself when the ports are free.
rem If a port is already listening, that service is treated as external:
rem identified + health-checked, no log capture, never killed by this window.
start "AiliXiya :7860 (single window)" cmd /k "cd /d %~dp0 & .venv\Scripts\python.exe -u -m jarvis.main"

echo.
echo  One window: AiliXiya :7860. llama :8080 / GPT-SoVITS :9880 run as its children.
echo  Monitor page: http://127.0.0.1:7860/monitor (jarvis opens its own window for it).
exit /b 0
