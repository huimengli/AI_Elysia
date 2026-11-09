@echo off
rem ────────────────────────────────────────────────
rem  start_all.bat — one-click launch of llama.cpp + GPT-SoVITS + Jarvis (爱莉希雅)
rem  :8080 llama.cpp | :9880 GPT-SoVITS | :7860 Jarvis Web UI
rem ────────────────────────────────────────────────
chcp 65001 >nul
cd /d "%~dp0"

rem ── writable matplotlib cache (kills the "WinError 5 / AppData\Local\matplotlib" warning) ──
set "MPLCONFIGDIR=%~dp0.tmp\mplconfig"
if not exist "%~dp0.tmp\mplconfig" mkdir "%~dp0.tmp\mplconfig"

rem ── port checks ──
netstat -ano | findstr ":8080 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo [Warn] :8080 already in use - llama.cpp may already be running.
)
netstat -ano | findstr ":9880 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo [Warn] :9880 already in use - GPT-SoVITS may already be running.
)
netstat -ano | findstr ":7860 " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo [Warn] :7860 already in use - Jarvis may already be running.
)

rem ── 1/3 llama.cpp (LLM, :8080) ──
if not exist "%~dp0llm\llama-b12144-bin-win-vulkan-x64\llama-server.exe" (
    echo [Skip] llama-server.exe not found under llm\llama-b12144-bin-win-vulkan-x64
    goto :gsv
)
start "llama.cpp :8080" cmd /k (
    cd /d "%~dp0llm\llama-b12144-bin-win-vulkan-x64"
    set "GGML_VULKAN=1"
    llama-server.exe -m "%~dp0llm\models\Qwen3.5-2B-Q4_K_M.gguf" --host 127.0.0.1 --port 8080 -c 65536 -ngl 99 -fa 1 --load-mode none -b 1024 -ub 512 --no-cont-batching --parallel 1 --jinja --repeat-penalty 1.05 --reasoning-format deepseek --reasoning-preserve --cache-type-k q4_0 --cache-type-v q4_0 --mmproj "%~dp0llm\models\Qwen3.5-2B_mmproj-F16.gguf"
)

rem ── 2/3 GPT-SoVITS (TTS, :9880) ──
:gsv
start "GPT-SoVITS" cmd /k (
    cd /d "%~dp0GPT-SoVITS-main"
    ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py
)

rem ── 3/3 Jarvis (爱莉希雅, :7860) ──
start "AiliXiya" cmd /k (
    set "HF_ENDPOINT=https://hf-mirror.com"
    set "HF_HOME=%~dp0.hf-cache"
    set "HF_HUB_DISABLE_XET=1"
    "%~dp0.venv\Scripts\python.exe" -u -m jarvis.main
)

echo.
echo  Launched: llama.cpp :8080 | GPT-SoVITS :9880 | Jarvis Web UI :7860
echo  Keep the three console windows open; closing a window stops that service.
exit /b 0
