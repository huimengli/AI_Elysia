# Progress — 跨会话进度台账

## 2026-10-12（Asia/Shanghai）

### 12:28 运行 Jarvis 项目（records/2026-10-12-12-28-30.md）

- 需求：把本项目跑起来；不装 Ollama，LLM 指向已运行的 llama.cpp `http://127.0.0.1:8080`（Qwen3.8-27B GGUF，OpenAI 兼容）。
- 环境：Python 3.12.0（`C:\Users\楼听\AppData\Local\Programs\Python\Python312\python.exe`）；Ollama 未安装（按要求不装）；llama.cpp 在 8080 正常运行，`/v1/models` 确认模型可用。
- 已完成：
  - `.venv` 创建（Python 3.12）。
  - `config.yaml`：新增 `llamacpp` provider 并设为 active；`wake_word.model` 改为内置 `jarvis`（自定义 `hey_jarvis.onnx` 不在仓库/openWakeWord 发行包内）。
  - 落盘 records/todo/progress/tree。
- 进行中：
  - pip 安装 requirements（后台作业 pwsh-64）。前两次失败根因：沙箱拒绝写 AppData pip 缓存（`WinError 5`，升级权限后仍复现）→ 改用 `PIP_CACHE_DIR=<workspace>\.pip-cache` 绕过。已确认 PyAudio 0.2.14 有 cp312 win_amd64 wheel，requirements.txt 原样可用。
- 待办：下载 openWakeWord ONNX 模型 → 启动 `python -m jarvis.main` → 验证 :7860 Web UI 与 llama.cpp 聊天链路。
- 15:00 复查：llama.cpp `/v1/models` 正常（Qwen3.8-27B GGUF，n_ctx 48128）。
- 16:10 依赖安装完成（清华镜像 `pypi.tuna.tsinghua.edu.cn`；阿里云镜像在 torch 124MB 下载中两次卡死且 pip `--timeout` 未生效；curl 在沙箱内 TLS 失败 SEC_E_NO_CREDENTIALS）。全部包成功，核心模块导入验证通过（IMPORTS_OK）。
- 16:30 openWakeWord 9 个 ONNX 模型下载完成（GitHub 直连 TLS 证书校验失败 → `_oww_dl.py` urllib `ssl.CERT_NONE` 回退 + GitHub API 大小校验，全部通过）；`Model(wakeword_models=["jarvis"])` 加载报 EACCES → 根因：CWD 存在同名 `jarvis/` 包目录，`os.path.exists("jarvis")` 为真导致把目录当 ONNX 加载（hard_bug.md HB-001）→ config 改 `wake_word.model: hey_jarvis_v0.1`，加载验证 OWW_OK。
- 16:50 首次启动 `python -m jarvis.main`：Web 服务已起（[Web] Event loop captured），TTS 问候阶段 `import kokoro` 链中 `MemoryError`（re/_parser.py）→ 系统内存耗尽（llama.cpp 27B 8.7GB BF16 常驻 + torch + 各原生库并发）。用户反馈：程序把内存和显存都撑爆，已手动重启 llama.cpp。
- 17:10 复查：llama.cpp 重启后 `/health` ok、`/v1/models` 模型已加载（BF16 8.7GB, n_ctx 48128）；系统可用内存 6.2 GB；`.hf-cache` 尚不存在（上次崩在 import 阶段，Kokoro 未及下载）。
- 17:20 策略调整：先以轻量脚本 `_precache.py`（仅 huggingface_hub，不载 torch）预下载 `hexgrad/Kokoro-82M` + `Systran/faster-whisper-small` 到工作区 `.hf-cache`（HF_ENDPOINT=hf-mirror.com），再启动 Jarvis，降低主进程峰值内存。首跑失败：huggingface_hub 2.2.0 新 xet/CAS 通道经镜像 401 → 设 `HF_HUB_DISABLE_XET=1` 回退经典 LFS 重跑（作业 pwsh-11）。
- 17:40 预下载完成（Kokoro-82M 72 文件 + faster-whisper-small 6 文件，PRECACHE_ALL_OK）。
- 18:xx espeakng_loader DLL **硬编码**数据目录 `D:/a/espeakng-loader/.../share/espeak-ng-data`（忽略路径参数与 env），缺数据即硬杀进程 → 用户批准后创建该目录并复制 364 个数据文件；espeak v1.52.0 初始化成功。副作用：同进程第二个 EspeakWrapper 返回 0 voices → Kokoro OOD 回退禁用（非致命，仅警告）。
- 19:xx–20:0x TTS 阻塞于 spacy `en_core_web_sm` 下载（GitHub 全阻）→ HF-mirror `spacy/en_core_web_sm` wheel（内部版本 3.7.1）改名后 `--no-index --no-deps` 装入 .venv，spacy 3.8.16 加载验证通过（仅 W095 警告）。
- 20:1x `_tts_test.py` 端到端 TTS 合成通过（TTS_TEST_OK chunks=1；期间 free 内存 ~400MB/load 98%，HB-003 风险实证）。
- 20:13 Jarvis 后台启动成功（作业 pwsh-50）：Web UI :7860 HTTP 200 ✓。
- 20:2x WS 聊天链路验证（`_ws_chat_test.py`）：connected/user/status 正常，但 LLM 回复为 Ollama 兜底错误 → 排查发现**所有 llama 服务已停**：8080 被 Steam（steamwebhelper ×4 ~1.95GB）占用，8090 等端口无监听；系统内存 free=593MB/20GB（load 97%）。
- 20:2x 落盘 HB-004 + need_user.md Q1（LLM 恢复方案 A/B/C/D，status: wait）；todo.md 同步。**当前阻塞：LLM 端到端验证**（等用户释放内存并选择模型/端口）。
- 20:3x 收尾：删除 12 个临时脚本 + spacy wheel + 14 个已关闭日志（保留 `_ws_chat_test.py` 与运行中的 `.jarvis-run.log`）。

### 2026-10-13 续
- 09:52 过夜复查：机器已重启（昨夜后台作业清除，Jarvis PID 11680 退出）；free=5274MB / load=74%；7860/8080/8090 全关；Steam 与身份不明系统 Python 消失。
- 09:52 用户答复 need_user.md Q1：llama.cpp 由用户自行启动，需要时 agent 发出请求 → Q1 status: done，归档 `ai_buckup/need_user.md_2026-10-13-09-56-54.md`。
- 09:56 后台重启 Jarvis（作业 pwsh-2）：:7860 HTTP 200 ✓（python PID 10480，~1.3GB）。
- 10:3x 用户启动 llama.cpp 于 **:8080**（模型与 config.yaml 完全一致，零改动）→ `_ws_chat_test.py` 端到端 **CHAT_OK** ✓（Qwen 真实回复，非 Ollama 兜底）。HB-004 解除。
- 10:4x 收尾：删除临时验证脚本，todo/progress/hard_bug/tree 同步，最终本地 commit（不 push）。**需求"将 Jarvis 项目运行起来"已完成。**

## 2026-10-13 下午（11:45–12:5x）

- 11:45 span："Stopped." 根因 = 非流式 + 60s 超时 → main.py 改 `stream=True` + timeout 300s（HB-005）；重启漏 HF env 致启动即崩（HB-006）→ 正确 env 重启恢复；唤醒词诊断峰值 0.985/0.790 ≫ 0.5（链路正常，待用户实测）。
- 11:55 GPT-SoVITS 任务（records/2026-10-13-11-55.md）：仓库 zip 经 ghproxy.net 下载解包 `GPT-SoVITS-main/`；爱莉希雅 v2 权重复制到位；**C 盘写满事故**（剩 10MB → 清 `.venv-gsv`/zip/`.pip-cache` 释放 ~4.3GB，现余 5.26GB）；预训练基座全部就位（gsv-v2final GPT 155MB + SoVITS 106MB + hubert 189MB + roberta 651MB）。
- 12:3x LLM 慢修复：Qwen3.8 thinking 模式 + 无 max_tokens → iGPU 无限生成（e2e 挂 40+min）→ config `max_tokens: 2048` + `enable_thinking: false`，main.py 传 `chat_template_kwargs`（HB-008）。
- 12:4x Jarvis 重启（pwsh-52，`-m jarvis.main`，HF env）；`_e2e_stream_test.py` e2e **PASS**（case1 71.5s / case2 40.1s，均真实回复，此前挂起 40+min）。
- 12:4x `jarvis/tts.py` 双 provider 化（kokoro 默认 / gptsovits：urllib GET api_v2 `/tts` + wave 解析 PCM，流式=逐句调用）；config.yaml 加 `tts.provider` + `tts.gptsovits` 块（ref=爱莉希雅【感动】wav）。
- .gitignore 追加 `.venv-gsv/`、`GPT-SoVITS-main/`、`_*.py`。
- 新增 HB-007（chroma 默认 embedding 目录 `C:\Users\楼听\.cache\chroma` PermissionError，记忆入库失败，不阻塞主链路）→ need_user.md **Q2 待用户决策**（A 修 ACL / B 改显式本地 embedding / C 降级 warning）。
- 进行中：pwsh-50 `.venv-gsv`（torch CPU + requirements）；之后 api_v2.py :9880 推理验证（**需用户先停 llama :8080，HB-003**）→ provider 切换 + e2e。

## Git 提交记录

- `7d279a7`（2026-10-13-10:4x，main）`docs(AI): 补全 Jarvis 运行记录并归档 Q1（端到端 CHAT_OK）`——9 files, +273/−2：records/、hard_bug.md、need_user.md（+ai_buckup 归档）、progress/todo/tree、config.yaml、.gitignore。**已本地 commit，未 push。**
