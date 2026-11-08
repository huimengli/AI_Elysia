# =====================================================================
#  llama-server 启动脚本 (vulkan)
#  Qwen3.5-2B-Q4_K_M GGUF 模型（默认；-Model 可改）
# =====================================================================
# 用法:
#   .\start-llama-server.ps1                    默认启动 (网页 http://127.0.0.1:8080)
#   .\start-llama-server.ps1 -Port 8081         改端口
#   .\start-llama-server.ps1 -Ctx 32768         改上下文长度 (KV cache 大小随之变化)
#   .\start-llama-server.ps1 -NGL 99            指定卸载到 GPU 的层数
#   .\start-llama-server.ps1 -T 8               指定 CPU 线程数
#
# 注意:
#   - 脚本只做"前台运行"。要让它常驻/后台跑，请看脚本末尾的说明。
#   - 运行前确保 Ollama 没有占用 8080 端口 (或换 -Port)。
# =====================================================================
param(
    [int]$Port = 8080,
    [int]$Ctx = 65536,          # 上下文长度 (影响 KV cache 大小)
    [int]$NGL = 99,             # 卸载到 GPU 的层数 (99 = 全部层尽量上 GPU)
    [string]$Host_ = "127.0.0.1",
    [int]$T = 0,                 # CPU 线程数, 0 = 自动
    [string]$Model = $(Join-Path -Path $PSScriptRoot -ChildPath "models\Qwen3.5-2B-Q4_K_M.gguf"),
	[string]$ImageModel = $(Join-Path -Path $PSScriptRoot -ChildPath "models\Qwen3.5-2B_mmproj-F16.gguf"),
	[int]$MTP = 0,				# 是否启用多令牌预测(0为不启动)
	[string]$Key = "", 			# 是否启用API_KEY
	[int]$B = 1024,
	[int]$UB = 512
)

# ---- 路径 --------------------------------------------------------------
# BinDir 用仓库内启动器（随 llm/ 文件夹放置，已被 .gitignore 排除）
$BinDir  = Join-Path $PSScriptRoot "llama-b12144-bin-win-vulkan-x64"

$Server = Join-Path $BinDir "llama-server.exe"
if (-not (Test-Path $Server)) {
    Write-Error "找不到 $Server`n请确认 vulkan 版已编译到 $BinDir"
    exit 1
}
if (-not (Test-Path $Model)) {
    Write-Error "找不到模型 $Model"
    exit 1
}

# ---- 环境 (加入 vulkan 运行时 + llama 后端 DLL 目录) ----------------------
$env:PATH = "$BinDir;$env:PATH"
$env:GGML_Vulkan = "1"   # 提示 vulkan 后端
$env:GGML_VK_VISIBLE_DEVICES = "0" # 表示使用第一块设备
$env:AMD_VULKAN_ASYNC_COMPUTE = "1"
$env:RADV_PERFTEST = "aco,ngg,sam,rt"

# 切到 bin 目录, 确保 ggml-vulkan.dll 等动态库能被加载
Push-Location $BinDir

Write-Host ""
Write-Host "============================================================"
Write-Host "  llama-server  (vulkan)"
Write-Host "  模型     : $Model"
Write-Host "  端口     : http://${Host_}:$Port"
Write-Host "  上下文   : $Ctx  tokens  (KV cache 因此而定)"
Write-Host "  GPU 层数 : $NGL "
Write-Host "  CPU 线程 : $(if($T){$T}else{'自动'})"
Write-Host "  多令牌   : $(if($MTP){[string]$MTP+'个草稿'}else{'不启用'})"
Write-Host "  视觉支持 : $(if($ImageModel -eq ''){'不启用'}else{$ImageModel})"
Write-Host "  密钥     : $(if($Key -eq ''){'不启用'}else{'启用'})"
Write-Host "============================================================"
Write-Host "  网页界面      -> http://${Host_}:$Port"
Write-Host "  OpenAI API    -> http://${Host_}:$Port/v1/chat/completions"
Write-Host "============================================================"
Write-Host "  按 Ctrl + C 停止"
Write-Host ""

# ---- 组装参数 ------------------------------------------------------------
$llamaArgs = @(
    "-m", $Model,
    "--host", $Host_,
    "--port", $Port,
    "-c", $Ctx,
    "-ngl", $NGL,
	"-fa", "1", 						# 启用Flash Attention(1=开启,注意力优化机制,减少显存使用并加速)
	"--load-mode", "none", 				# 减少内存占用
	# 减少 CPU 和 GPU 的临时缓冲
	"-b", $B,
	"-ub", $UB,
	"--no-cont-batching",
	# 单槽位
	"--parallel", "1",
	"--jinja", 							# 使用jinja模板
	"--repeat-penalty", "1.05"  		# 轻微的重复惩罚，防止高温度下产生死循环
	"--reasoning-format", "deepseek" 	# 解析/格式化推理内容以匹配DeepSeek的API结构
	"--reasoning-preserve"
	# KV cache 也用Q4量化
    "--cache-type-k", "q4_0",
    "--cache-type-v", "q4_0"
	# "--no-reasoning-effort-check"
)
# 添加视觉模型
if ($ImageModel -ne "") {
	$llamaArgs += "--mmproj"
	$llamaArgs += $ImageModel
}
# 添加API_KEY
if ($Key -ne "") {
	$llamaArgs += "--api-key"
	$llamaArgs += $key
}
# MTP支持
if ($MTP -gt 0) {
	$llamaArgs += "--spec-type"
	$llamaArgs += "draft-mtp,ngram-mod"
	$llamaArgs += "--spec-draft-n-max"
	$llamaArgs += $MTP
}
if ($T -gt 0) { $llamaArgs += "-t"; $llamaArgs += $T }

& $Server @llamaArgs

# ---- 常驻/后台运行的方法 -----------------------------------------------
<#
  以上 & $Server 是前台运行, 关掉终端进程即结束。
  想后台常驻 (关掉窗口也继续服务), 把上面的 "& $Server @args" 替换为:

       Start-Process -FilePath $Server -ArgumentList $llamaArgs -WindowStyle Hidden

  (然后此脚本会立即返回, 服务仍在后台。想看日志可加 -RedirectStandardOutput)

  注意: Start-Process 传 -ngl 99 等参数时, 若含需引号的值需用数组拼接得很小心;
        也可直接用 Start-Process 一行式。
#>