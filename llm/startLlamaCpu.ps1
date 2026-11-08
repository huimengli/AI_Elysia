# =====================================================================
#  llama-server 启动脚本 (纯 CPU 版)
#  用途: 与游戏共存时不占用/不污染显存 —— 集显共享显存会被 GPU offload 抢用,
#        表现为游戏画面闪动、色彩条纹 (hard_bug.md HB1)。
#  模型: models\Qwen3.5-2B-Q4_K_M.gguf + models\Qwen3.5-2B_mmproj-F16.gguf (视觉)
# =====================================================================
# 用法:
#   .\startLlamaCpu.ps1                     默认启动 (http://127.0.0.1:8080)
#   .\startLlamaCpu.ps1 -Port 8081          改端口
#   .\startLlamaCpu.ps1 -Ctx 8192           改上下文长度
#   .\startLlamaCpu.ps1 -T 12               指定 CPU 线程数 (0 = 自动)
#   .\startLlamaCpu.ps1 -NGL 1              把 1 层 offload 到 GPU (默认 0 = 纯 CPU)
#
# 注意:
#   - 纯 CPU 不碰显存，游戏画面不会受影响；代价是速度慢，一次读图数十秒。
#   - 视觉模型必须带 --mmproj，否则没有图像输入能力。
# =====================================================================
param(
    [int]$Port = 8080,
    [int]$Ctx = 65536,
    [int]$NGL = 0,
    [string]$Host_ = "127.0.0.1",
    [int]$T = 0,
    [string]$Model = $(Join-Path -Path $PSScriptRoot -ChildPath "models\Qwen3.5-2B-Q4_K_M.gguf"),
    [string]$ImageModel = $(Join-Path -Path $PSScriptRoot -ChildPath "models\Qwen3.5-2B_mmproj-F16.gguf"),
    [string]$Key = "",
    [int]$B = 1024,
    [int]$UB = 512
)

# ---- 路径 --------------------------------------------------------------
# BinDir 用仓库内启动器（随 llm/ 文件夹放置，已被 .gitignore 排除）
$BinDir = Join-Path $PSScriptRoot "llama-b12144-bin-win-cpu-x64"

$Server = Join-Path $BinDir "llama-server.exe"
if (-not (Test-Path $Server)) {
    Write-Error "找不到 $Server`n请确认 CPU 版在 $BinDir"
    exit 1
}
if (-not (Test-Path $Model)) {
    Write-Error "找不到模型 $Model"
    exit 1
}

# CPU 构建没有 Vulkan 后端；显式清掉 GPU 相关环境变量，避免继承 Vulkan 脚本的设置
$env:GGML_Vulkan = $null
$env:GGML_VK_VISIBLE_DEVICES = $null
$env:AMD_VULKAN_ASYNC_COMPUTE = $null
$env:RADV_PERFTEST = $null
if ($NGL -gt 0) {
    # 本脚本是 CPU 构建，任何 >0 的 NGL 都无意义（ggml 无 GPU 后端，层会回到 CPU）。
    Write-Warning "-NGL $NGL 在 CPU 构建下无效，仍按纯 CPU 运行。要 GPU offload 请用 startLlama.ps1 (Vulkan)。"
    $NGL = 0
}

Push-Location $BinDir

Write-Host ""
Write-Host "============================================================"
Write-Host "  llama-server  (纯 CPU)"
Write-Host "  模型     : $Model"
Write-Host "  视觉     : $(if($ImageModel -eq ''){'不启用'}else{$ImageModel})"
Write-Host "  端口     : http://${Host_}:$Port"
Write-Host "  上下文   : $Ctx  tokens"
Write-Host "  GPU 层数 : $NGL  (0 = 不占显存)"
Write-Host "  CPU 线程 : $(if($T){$T}else{'自动'})"
Write-Host "  密钥     : $(if($Key -eq ''){'不启用'}else{'启用'})"
Write-Host "============================================================"
Write-Host "  网页界面      -> http://${Host_}:$Port"
Write-Host "  OpenAI API    -> http://${Host_}:$Port/v1/chat/completions"
Write-Host "============================================================"
Write-Host "  按 Ctrl + C 停止"
Write-Host ""

# ---- 组装参数 ------------------------------------------------------------
# CPU 说明:
#  - -ngl 0: 全部层在 CPU，显存零占用，游戏画面不受影响。
#  - -fa 0: CPU 构建没有 flash-attention 路径，关掉。
#  - KV cache 保持默认精度 (f32)：CPU 上 q4_0 KV 只会降质量，不省显存。
$llamaArgs = @(
    "-m", $Model,
    "--host", $Host_,
    "--port", $Port,
    "-c", $Ctx,
    "-ngl", $NGL,
    "-fa", "0",
    "-b", $B,
    "-ub", $UB,
    "--no-cont-batching",
    "--parallel", "1",
    "--jinja",
    "--repeat-penalty", "1.05",
    "--reasoning-format", "deepseek",
    "--reasoning-preserve"
)

if ($ImageModel -ne "") {
    $llamaArgs += "--mmproj"
    $llamaArgs += $ImageModel
}
if ($Key -ne "") {
    $llamaArgs += "--api-key"
    $llamaArgs += $Key
}
if ($T -gt 0) { $llamaArgs += "-t"; $llamaArgs += $T }

& $Server @llamaArgs

Pop-Location

# ---- 常驻/后台运行的方法 -----------------------------------------------
# 前台运行，关窗口即结束。要后台常驻:
#   Start-Process -FilePath $Server -ArgumentList $llamaArgs -WindowStyle Hidden
#   (加 -RedirectStandardOutput 可看日志)
