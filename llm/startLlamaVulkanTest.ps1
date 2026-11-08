# startLlamaVulkanTest.ps1 — GPU 加速读图的受控试验（小 offload + 规避集显 cooperative-matrix）
# 目的：**decode 留 CPU，视觉塔进 VRAM**。llama.cpp 的 offload 从底层向上，视觉塔/嵌入层需要 -ngl>=1 且 -fa 1
# 才会走 GPU；-ngl 1 是最小侵入（约 200MB 级），图像编码与 prompt 处理上 GPU，生成仍在 CPU。
# 判定方法：同一张整屏截图，比较 timings.promptTokPerSec（-ngl 0 基线 vs -ngl 1）与 tokPerSec（应基本不变，CPU 约 29）。
# 与 HB1 的关系：集显 780M 与游戏共用物理内存池，大缓冲 + cooperative-matrix 是已知污染游戏帧缓冲的路径。
# 用法：powershell -NoProfile -File startLlamaVulkanTest.ps1            # -ngl 2，-fa 1
#       powershell -NoProfile -File startLlamaVulkanTest.ps1 -NGL 0     # 回 CPU 基线（用 Vulkan 构建，CPU 推理）
# 启动后先看游戏画面：出现闪动/色彩条纹立刻 Ctrl+C 停掉（用 wow_observe / wow_wait 确证）。

param(
    [int]$Port = 8080,
    [int]$Ctx = 8192,
    [int]$T = 8,
    [int]$NGL = 1,
    [string]$Model = $(Join-Path $PSScriptRoot 'models\Qwen3.5-2B-Q4_K_M.gguf'),
    [string]$ImageModel = $(Join-Path $PSScriptRoot 'models\Qwen3.5-2B_mmproj-F16.gguf'),
    [string]$Key = '',
    [int]$B = 2048,
    [int]$UB = 2048
)

$BinDir = Join-Path $PSScriptRoot 'llama-b12144-bin-win-vulkan-x64'
$Exe = Join-Path $BinDir 'llama-server.exe'

if (-not (Test-Path $Exe)) { throw "llama-server 不存在: $Exe" }

# 切到 bin 目录，确保 ggml-vulkan.dll / llama-server-impl.dll 可被加载（与 startLlama.ps1 一致）
Push-Location $BinDir

# 规避集显 cooperative-matrix 已知路径；清掉 Linux radv 残留变量（Windows 无效）
$env:GGML_VK_DISABLE_COOPERATIVE_MATRIX = '1'
$env:GGML_VK_VISIBLE_DEVICES = '0'
Remove-Item Env:\RADV_PERFTEST -ErrorAction SilentlyContinue
Remove-Item Env:\AMD_VULKAN_ASYNC_COMPUTE -ErrorAction SilentlyContinue
Remove-Item Env:\GGML_Vulkan -ErrorAction SilentlyContinue

Write-Host "Vulkan 构建 + 小 offload（NGL=$NGL）"
Write-Host "  GGML_VK_DISABLE_COOPERATIVE_MATRIX=1（规避集显 cooperative-matrix 路径）"
Write-Host "  显存账：2B Q4_K_M 约 1.2GB + mmproj-F16 约 0.62GB + KV（Ctx=$Ctx）"
if ($NGL -ge 8) {
    Write-Warning "NGL>=8 会把大量层压进集显共享池，与游戏争用（HB1 现场）；试验期请保持 NGL<=4。"
}

$args0 = @(
    '-m', $Model,
    '--host', '127.0.0.1',
    '--port', $Port,
    '-c', $Ctx,
    '-ngl', $NGL,
    '-fa', '1',
    '-b', $B,
    '-ub', $UB,
    '-t', $T,
    '--parallel', '1',
    '--no-cont-batching',
    '--jinja',
    '--repeat-penalty', '1.05',
    '--mmproj', $ImageModel
)

# 添加API_KEY
if ($Key -ne "") {
	$args0 += '--api-key'
	$args0 += $Key
}

& $Exe @args0

Pop-Location
