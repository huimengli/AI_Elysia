@echo off
rem ────────────────────────────────────────────────
rem  start_all.bat — one-click launch of GPT-SoVITS + Jarvis (爱莉希雅)
rem  llama.cpp (:8080) is intentionally NOT started here — start it yourself.
rem ────────────────────────────────────────────────
chcp 65001 >nul
cd /d "%~dp0"

rem ── port checks ──
netstat -ano | findstr ":9880 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo [Warn] :9880 already in use — GPT-SoVITS may already be running.
)
netstat -ano | findstr ":7860 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo [Warn] :7860 already in use — Jarvis may already be running.
)

rem ── 1/2 GPT-SoVITS (TTS, :9880) ──
start "GPT-SoVITS" cmd /k (
    cd /d "%~dp0GPT-SoVITS-main"
    ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py
)

rem ── 2/2 Jarvis (爱莉希雅, :7860) ──
start "AiliXiya" cmd /k (
    set "HF_ENDPOINT=https://hf-mirror.com"
    set "HF_HOME=%~dp0.hf-cache"
    set "HF_HUB_DISABLE_XET=1"
    "%~dp0.venv\Scripts\python.exe" -u -m jarvis.main
)

echo.
echo  Launched: GPT-SoVITS :9880 | Jarvis Web UI :7860
echo  Please start llama.cpp :8080 separately if you have not already.
exit /b 0
