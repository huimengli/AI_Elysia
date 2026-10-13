# Hard Bug 记录

## HB-001 openWakeWord 模型名与 CWD 目录冲突（已解决）

- 时间：2026-10-12-16-19
- 状态：已解决
- 影响：`python -m jarvis.main`（CWD=项目根）下唤醒词加载必然崩溃，openWakeWord `Model(wakeword_models=["jarvis"])` 报 `Load model from jarvis failed: system error number 13`（EACCES）。
- 现象：onnxruntime 尝试把项目根目录下的 `jarvis/` 包目录当作 ONNX 文件加载。
- 尝试：
  1. 确认模型文件可读、大小与 GitHub API 元数据一致 → 排除文件本身问题。
  2. 绝对路径 `ort.InferenceSession(...)` 直接加载成功 → 排除 onnxruntime/沙箱问题。
  3. 复现 openwakeword 名称解析逻辑 → 定位根因。
- 根因：`openwakeword/model.py` 中 `os.path.exists("jarvis")` 相对 CWD 解析；项目根存在 `jarvis/` 包目录 → 命中"已存在路径"分支，跳过预训练模型名解析，把目录名当模型路径传给 onnxruntime。
- 方案：`config.yaml` 中 `wake_word.model` 改为完整预训练名 `hey_jarvis_v0.1`（CWD 下无同名条目，正常解析到 `resources/models/hey_jarvis_v0.1.onnx`）。验证：`Model(wakeword_models=['hey_jarvis_v0.1'])` 加载 + 推理成功（噪声输入得分 0.0）。
- 关联需求：records/2026-10-12-12-28-30.md
- 备注：若未来新增自定义唤醒词（如 `ailixiya.onnx`），模型名同样需避免与 CWD 下条目重名。

## HB-002 huggingface_hub 2.x xet/CAS 通道经镜像 401（已解决）

- 时间：2026-10-12-17-18
- 状态：已解决
- 影响：`HF_ENDPOINT=https://hf-mirror.com` 下 `snapshot_download` 下载 LFS 大文件（如 `kokoro-v1_0.pth`、`model.bin`）失败，小文件正常。
- 现象：`RuntimeError: Task error: File reconstruction error: CAS Client Error: Request error: HTTP status client error (401 Unauthorized), domain: https://cas-server.xethub.hf.co/v2/reconstructions/...`
- 根因：huggingface_hub 2.2.0 对 LFS 文件默认走新 xet/CAS 通道（xethub.hf.co），该域名不经 hf-mirror 代理且匿名请求被拒。
- 方案：环境变量 `HF_HUB_DISABLE_XET=1`（`constants.py` 定义，`file_download.py` 据此回退经典 LFS resolve 路径）。已在 `_precache.py` 中固化。
- 关联需求：records/2026-10-12-12-28-30.md

## HB-003 Jarvis 与 llama.cpp 27B 并存内存耗尽（部分解决）

- 时间：2026-10-12-16-50
- 状态：部分解决（策略缓解，根因是系统物理内存不足，需用户知悉）
- 影响：`python -m jarvis.main` 启动阶段 `import kokoro → misaki → spacy` 链中 `MemoryError`，进程退出；同时把 llama.cpp 的内存/显存撑爆（用户反馈并重启了 llama.cpp）。
- 现象：Web 服务已起（[Web] Event loop captured）后 TTS 问候崩溃；llama.cpp 重启前 `/v1/models` 503。
- 根因：llama.cpp 27B BF16（8.7GB 常驻内存/显存）+ Jarvis 侧 torch + Kokoro + faster-whisper + 各原生库并发，超出系统可用物理内存。
- 方案：
  1. 用户重启 llama.cpp 释放内存后启动 Jarvis（当前可用约 6.2 GB）。
  2. 用轻量 `_precache.py` 预下载 TTS/STT 大模型到 `.hf-cache`，避免主进程"边下载边加载"的峰值。
  3. 若仍 OOM：建议用户降低 llama.cpp 占用（减小 `-c` 上下文、减少 GPU 层 `-ngl`）或错峰运行。
- 关联需求：records/2026-10-12-12-28-30.md

## HB-004 LLM 服务全部停摆且系统内存耗尽（未解决，需用户决策）

- 时间：2026-10-12-20-25
- 状态：未解决（阻塞 Jarvis 端到端验证；已写入 need_user.md Q1）
- 影响：Jarvis Web UI / WS / TTS 均已正常，但 LLM 调用失败——主 provider 异常后落入 Ollama 兜底并同样失败，WS 返回 "Failed to connect to Ollama"。
- 现象与排查：
  1. `http://127.0.0.1:8080/` 返回 "CEF remote debugging" 页面 → 8080 现被 **Steam（steamwebhelper，4 实例共 ~1.95GB）** 占用，原 Qwen llama.cpp server 已停止。
  2. 端口探测：8090 / 8081 / 8082 / 8085 / 1234 / 5000 / 11434 均未监听；无 llama 相关进程。
  3. `F:\魔搭社区\Bonsai_2_27B\` 项目日志显示其 llama-server（Vulkan，Ternary-Bonsai-2-27B）上次成功监听 :8090，当前未运行；启动脚本注明"8080 已被 Steam 占用，故使用 8090"。
  4. 内存：free=593MB / total=20286MB / load=97%（GlobalMemoryStatusEx）。Jarvis 进程工作集被压缩（大量换页）。
  5. 另发现身份不明的系统 Python（Python312，~1.4GB，与 Jarvis 同秒启动；CIM/WMIC 在沙箱内不可用，无法取命令行）——来源待用户确认。
- 结论：当前空闲内存不足以加载任何 27B GGUF（最小候选 `Qwen3.8-27B-UD-IQ2_XXS.gguf` 6.77GB；配置中 IQ2_XS-mtp 8.17GB）。立即启动必复现 HB-003 式 OOM。
- 方案：见 need_user.md Q1（用户释放内存后由 agent 启动 / 改用小模型 / 用 Bonsai 模型 / 用户自启报端口）。启动端口需避开 8080（Steam），候选 8090；确定后同步修改 `config.yaml` llm.providers.llamacpp.base_url。
- 关联需求：records/2026-10-12-12-28-30.md

### HB-004 状态更新（2026-10-13-09:57）

- 机器重启后内存缓解：free=5274MB / load=74%；Steam（原 :8080 占用方）与身份不明系统 Python 已消失，8080/8090 均空闲。
- need_user.md Q1 已获用户答复并归档：llama.cpp 由**用户自行启动**，agent 需要时发出请求（建议模型 `Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_XS-mtp.gguf`、端口 8090、上下文 ≤16384）。
- 当前状态：仍阻塞"LLM 端到端验证"，等待用户启动 llama.cpp；Jarvis 本体已于 10-13 重启（作业 pwsh-2，:7860 ✓）。

### HB-004 解决（2026-10-13-10:3x）

- 用户启动 llama.cpp 于 **:8080**（模型 `Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_XS-mtp.gguf`，n_ctx 48128），与 `config.yaml` 完全一致，配置零改动。
- `_ws_chat_test.py` 端到端复跑 **CHAT_OK**：WS connected → chat → user/status → `response`（Qwen 真实中文回复，非 Ollama 兜底错误）。
- 状态：**已解决**。注意 HB-003（内存紧张）仍潜在存在：27B 模型常驻 ~8.8GB，系统再开重负载时可能复现 OOM——启动 llama 前留意可用内存。

## HB-005 非流式 LLM 调用 + 60s 超时 → Web UI 只见 "Stopped."（已解决）

- 时间：2026-10-13-11-50
- 状态：已解决（修复已实施，e2e 验证进行中）
- 影响：llama.cpp iGPU ~1 tok/s 时，任何超过 60s 的生成被 `OpenAI(timeout=60.0)` 直接掐断；且非流式期间 UI 零反馈，用户以为卡死点 ABORT → `abort_all()` → 回 "Stopped."（web.py:213），两条中文消息均不命中 `_is_stop_command`（仅精确英文匹配）。
- 现象：Web UI 发 "你听不见我讲话吗?" / "你好?"，状态 SPEAKING + ABORT 可见，最终气泡只有 "Stopped."；llama `/health` 200（非 LLM 故障）。
- 根因：`_call_openai_provider` 一次性 `create()`（无 stream）+ 客户端 timeout=60s；短回复在 iGPU 上需 30-90s。
- 方案：`jarvis/main.py` — ① `_get_openai_client` timeout 60→300s；② `_call_openai_provider` 改 `stream=True`，按 chunk 累积 `delta.content` 与 `delta.tool_calls`（index 槽位 `{id,name,arguments}`），工具循环语义不变，每 chunk `_check_abort()`；保持最终 `response` 事件契约（UI 无 partial 处理）。
- 关联需求：records/2026-10-13-11-45.md

## HB-006 重启 Jarvis 漏设 HF env → Kokoro 启动即崩（已解决）

- 时间：2026-10-13-11-25
- 状态：已解决
- 影响：后台作业环境不继承交互 shell 的 `HF_HOME/HF_ENDPOINT`；漏设时 `KPipeline` 初始化 `hf_hub_download(config.json)` 直连 huggingface.co 被拒（WinError 10061），5 次重试后 `LocalEntryNotFoundError`，进程在问候语 TTS 处崩溃——该窗口内无任何进程监听唤醒词。
- 现象：作业 pwsh-16 启动即 exit 1；用户期间喊 "Hey Jarvis" 无响应。
- 根因：Kokoro 预训练文件只在工作区 `.hf-cache`（HB-002/预下载策略），默认 HF_HOME（用户目录）下无缓存。
- 方案：所有 Jarvis 启动命令必须带 `HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME=C:\Users\楼听\Desktop\git\JarvisAi\.hf-cache`、`HF_HUB_DISABLE_XET=1`（已按此重启，作业 pwsh-19，:7860 ✓）。后续若做启动脚本应固化这三个 env。
- 关联需求：records/2026-10-13-11-45.md

## HB-007 chroma 默认 embedding 下载目录 PermissionError（未解决，待用户决策）

- 时间：2026-10-13-12-35
- 状态：未解决
- 影响：唤醒处理 `_process_request` 末尾 `memory.extract_and_store_facts()` → chroma upsert 抛异常，整条请求在 TTS 之后失败（handle_wake 捕获并回 "Sorry, something went wrong."）。
- 现象：作业 pwsh-19 退出前 traceback：`chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2._download_model_if_not_exists` → `os.makedirs('C:\\Users\\楼听\\.cache\\chroma')` → `PermissionError: [WinError 5] 拒绝访问`。
- 根因（待验证）：chromadb 默认 ONNXMiniLM_L6_V2 embedding function 首次运行需下载 ~90MB onnx 模型到 `%USERPROFILE%\\.cache\\chroma`，该目录创建被拒（ACL 或目录状态异常）。此前记忆入库曾成功过（memory.db / chroma 目录已存在），说明模型文件曾在别处就位或目录权限近期变化。
- 方案候选：
  1. 用户侧修复 `C:\Users\楼听\.cache` ACL（管理员创建/授权）；
  2. `jarvis/memory.py` 改为显式 embedding_function（如指向工作区 `.hf-cache` 的本地模型），绕开默认下载路径；
  3. 记忆入库失败降级为 warning 不中断请求（治标）。
- 关联需求：records/2026-10-13-11-55.md

## HB-008 Qwen3.8 iGPU thinking 模式无限生成 → 单次请求挂起 40+ 分钟（已解决）

- 时间：2026-10-13-12-30
- 状态：已解决（修复已实施，e2e 复验进行中）
- 影响：llama.cpp (Qwen3.8-27B GGUF, iGPU) 上每次对话生成前大量 thinking token（~1 tok/s），且 `max_tokens` 未设限 → 单次 LLM 请求挂起数十分钟；Web UI 无 partial 输出，用户只能 ABORT。
- 现象：e2e WS 测试 case1 发送后 40+ 分钟无任何事件（作业 pwsh-31）；llama `/health` 正常。
- 根因：Qwen3 系列 chat template 默认开启 thinking（`/think` 隐式），iGPU 推理 ~1 tok/s 时 thinking 阶段可达数千 token；OpenAI 客户端未传 `max_tokens`，生成无上限。
- 方案：`config.yaml` llm 段新增 `max_tokens: 2048`、`enable_thinking: false`；`jarvis/main.py` `_call_llm` 读取两键并传入 `_call_openai_provider`，`create()` 增加 `max_tokens=max_tokens` 与 `extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}}`（llama.cpp 支持 chat_template_kwargs）。
- 关联需求：records/2026-10-13-11-55.md
