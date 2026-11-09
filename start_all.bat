@echo off
rem ============================================================
rem  start_all.bat - one-click launch: llama.cpp + GPT-SoVITS + Jarvis
rem  :8080 llama.cpp  |  :9880 GPT-SoVITS  |  :7860 Jarvis Web UI
rem  Every service gets its own console window opened via "start".
rem  File is ASCII only, CRLF line endings.
rem ============================================================
setlocal
cd /d %~dp0

rem ---- writable matplotlib cache (kills the WinError 5 AppData\Local\matplotlib warning) ----
set "MPLCONFIGDIR=%~dp0.tmp\mplconfig"
if not exist "%~dp0.tmp\mplconfig" mkdir "%~dp0.tmp\mplconfig"

rem ---- 1/4 llama.cpp (LLM, :8080) ----
netstat -ano | findstr ":8080" | findstr "LISTENING" >nul
if errorlevel 1 (
    if exist "%~dp0llm\llama-b12144-bin-win-vulkan-x64\llama-server.exe" (
        start "llama.cpp :8080" cmd /k "cd /d %~dp0llm\llama-b12144-bin-win-vulkan-x64 & set GGML_VULKAN=1 & llama-server.exe -m %~dp0llm\models\Qwen3.5-2B-Q4_K_M.gguf --host 127.0.0.1 --port 8080 -c 65536 -ngl 99 -fa 1 --load-mode none -b 1024 -ub 512 --no-cont-batching --parallel 1 --jinja --repeat-penalty 1.05 --reasoning-format deepseek --reasoning-preserve --cache-type-k q4_0 --cache-type-v q4_0 --mmproj %~dp0llm\models\Qwen3.5-2B_mmproj-F16.gguf"
    ) else (
        echo [Skip] llama-server.exe not found under llm\llama-b12144-bin-win-vulkan-x64
    )
) else (
    echo [Skip] :8080 already in use - llama.cpp is running.
)

rem ---- 2/4 GPT-SoVITS (TTS, :9880) ----
netstat -ano | findstr ":9880" | findstr "LISTENING" >nul
if errorlevel 1 (
    start "GPT-SoVITS :9880" cmd /k "cd /d %~dp0GPT-SoVITS-main & ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py"
) else (
    echo [Skip] :9880 already in use - GPT-SoVITS is running.
)

rem ---- 3/4 Jarvis (AiliXiya, :7860) ----
netstat -ano | findstr ":7860" | findstr "LISTENING" >nul
if errorlevel 1 (
    start "AiliXiya :7860" cmd /k "set HF_ENDPOINT=https://hf-mirror.com & set HF_HOME=%~dp0.hf-cache & set HF_HUB_DISABLE_XET=1 & cd /d %~dp0 & .venv\Scripts\python.exe -u -m jarvis.main"
) else (
    echo [Skip] :7860 already in use - Jarvis is running.
)

rem ---- 4/4 status panel window (ports + GET /api/health every 5 s) ----
start "Jarvis Status :7860" powershell -NoProfile -Command "while($true){$Host.UI.RawUI.WindowTitle='Jarvis Status';cls;Get-Date -Format 'HH:mm:ss';foreach($p in 8080,9880,7860){$l=Get-NetTCPConnection -LocalPort $p -State Listen -EA SilentlyContinue;if($l){'PORT '+$p+' LISTENING pid '+$l[0].OwningProcess}else{'PORT '+$p+' DOWN'}};try{(Invoke-WebRequest -Uri http://127.0.0.1:7860/api/health -UseBasicParsing -TimeoutSec 5).Content}catch{'health: unreachable'};Start-Sleep -Seconds 5}"

echo.
echo  Windows opened: llama.cpp :8080 / GPT-SoVITS :9880 / AiliXiya :7860 / Jarvis Status
echo  Keep the windows open; closing a window stops that service.
exit /b 0

