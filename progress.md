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
- 进行中：`.venv-gsv` requirements（pwsh-50 两轮超时失败 → `_setup_gsv2.py` 分三批重试，作业 pwsh-64，含 gyan.dev portable ffmpeg 入 `GPT-SoVITS-main/runtime/`）；`tts_infer.yaml` custom 段已指向爱莉希雅 e20/e24（CPU）；参考音频已复制 `GPT-SoVITS-main/ref_audio/Elysia_ref_gandong.wav`；`_tts_api_test.py` 冒烟脚本就绪。之后 api_v2.py :9880 推理验证（**need_user Q3：需用户先停 llama :8080，HB-003**）→ provider 切换 + e2e。

## 2026-10-13 晚间（17:0x–18:1x）

- 17:2x **Q2/HB-007 解决**：chroma 默认 embedding 模型硬编码下载 home `.cache`（沙箱不可写）→ 83MB ONNX 预下载工作区 `.chroma-models/`（SHA256 校验）+ `jarvis/memory.py` `WorkspaceMiniLM` 子类指路；旧空 chroma 库因 EF 配置冲突删除重建；实测 store/search OK。
- 17:3x **config.yaml 潜伏 bug**：双引号内未转义 `\B`（无效 YAML，任何进程重新加载即崩）→ 自 HEAD 恢复 + 改单引号；工作区文件 GBK/UTF-8 混合编码 → 纯 UTF-8，jarvis 全部 11 处 `open(config)` 补 `encoding="utf-8"`。
- 17:4x need_user **Q2/Q3 解决并归档**（Q3：用户已停 llama :8080，内存空出）；hard_bug.md 归档（HB-007 标记解决，仅留 HB-003 部分解决）。
- 17:5x GPT-SoVITS venv 安装：pwsh-77/89 连续在 jieba sdist 构建死挂 → 根因定位（PEP517 隔离构建在 `%LOCALAPPDATA%\Temp` 建临时 venv 被沙箱拦截；镜像确认 jieba/jieba_fast 零 wheel）→ `_setup_gsv4.py`（pwsh-105）：setuptools/wheel 预装 + `--no-build-isolation` 本地构建 jieba、jieba_fast 跳过（可选依赖）、其余纯 wheel 批次 → **ALL_BATCHES_DONE + GSV_IMPORTS_OK**（torch 2.14.1+cpu，18 模块导入通过）。
- 进行中：api_v2.py :9880 启动 → `_tts_api_test.py` 验证 → `tts.provider: gptsovits` 切换 + Jarvis 重启（HF env）→ `_e2e_stream_test.py` 复验。

## 2026-10-13 深夜（18:3x–20:1x）

- 18:3x GPT-SoVITS 仓库**整体同步为 current main 布局**（旧 zip 缺 `AR/`、`text/`，api_v2 sys.path 需要）；权重保持仓库根。
- 18:4x **HB-009 jieba_fast shim**：镜像零 wheel → 仓库根 `GPT-SoVITS-main/jieba_fast/` re-export shim（不动 site-packages）。
- 18:5x `tts_infer.yaml` custom 路径修正为 main 布局 → api_v2 确认加载 Elysia e20.ckpt + e24_s13080.pth（无 fall back 行）。
- 19:2x **HB-010**：/tts 400（torchaudio.load→torchcodec，镜像 0 win wheel）→ `TTS_infer_pack/TTS.py` 本地补丁 `_load_audio_compat()`（soundfile）。
- 19:3x **HB-011**：/tts 挂死（split_lang 硬编码 `model="full"` → fast_langdetect 下载 ~1GB，外网不可达）→ 仓库副本 `langsegmenter.py` 运行期 monkey-patch 为 lite（包内自带 938KB 量化模型）。
- 19:5x **api_v2 冒烟 PASS**：84.1s / 541KB WAV / **32kHz** mono / 8.5s——爱莉希雅声音可用（v2 VITS 输出 32k，非 24k；jarvis/tts.py 按 WAV 头采样率播放，已兼容）。
- 20:0x `config.yaml` 切 **`tts.provider: gptsovits`**；Jarvis 以 `.venv\Scripts\python.exe -u -m jarvis.main` + 三个 HF 环境变量重启（:7860，gptsovits 生效）。
- 20:1x `_tts_direct_test.py` **PASS**（Jarvis `_synth` → gptsovits：76.3s / 32kHz / 5.2s）——provider 切换 + API 集成验证完成。
- **当前阻塞**：llama :8080 处于用户停用状态 → 完整聊天 e2e（WS→LLM→爱莉希雅语音）需用户重启 llama → need_user.md **Q4**（status: wait）。

## 2026-10-13 深夜至凌晨（20:4x–21:1x）

- 20:4x 用户重启 llama-server（:8080，IQ2_XS-mtp 量化、ctx 16348）→ need_user **Q4 done**。首跑 e2e 两案例均 `Error: 'gbk' codec can't encode '\u21b5'` → `.jarvis-run.log` 定位两层问题：GBK print 崩溃掩盖真实 LLM 500（**HB-012**）+ llama.cpp 500（**HB-013**）。
- 20:5x **HB-013 根因**：Qwen3.8 新 chat template 拒绝任何非首位 system 消息（`raise_exception('System message must be at the beginning.')`）；经 `_gguf_template.py` 从 GGUF metadata 手工提取模板证实（该 GGUF 为 Swift 重打包非标准文件——字符串无 8 字节对齐，v3 header n_tensors 在前；模板存 `_chat_template.jinja`）。curl 矩阵验证：单 system OK / 双 system 必 500。
- 21:0x **修复**（`jarvis/main.py` 三处）：stdout/stderr `reconfigure(utf-8, errors=replace)`（HB-012）；facts 合并进主 system prompt 单条消息（HB-013）；`_strip_think` 增残留 ⌵/⌖ 清除。`_e2e_stream_test.py` PASS 判定加严（拒绝 `Error:`/codec 文本）。
- 21:1x **e2e 复验 PASS**（pwsh-200）：case1 自我介绍 70.0s / case2 时间问句 39.4s，均真实回答、无 GBK 错误。case2 未触发工具事件——系统提示词含 `Current date and time`，IQ2_XS 模型直接引用作答（答案正确），属模型行为差异非缺陷。
- 收尾：need_user.md 全量归档 `ai_buckup/need_user.md_2026-10-13-21-12-19.md`（Q2/Q3/Q4 均 done）；hard_bug.md 追加 HB-012/HB-013（已解决）；records/todo/tree 同步。**需求"接入 GPT-SoVITS 2.0 爱莉希雅 TTS"已完成**（端到端验收通过）。

## 2026-10-13 深夜至 2026-10-14（爱莉希雅化 + 自训唤醒词，records/2026-10-13-21-38-01.md）

- 21:3x 需求（6 项）：T1 自称"爱莉希雅" / T2 openwakeword-train 自训唤醒词 / T3 先落盘 / T4 仓库私有或描述改"自用" / T5 强制中文 / T6 网页 UI 爱莉希雅化（仅记 todo）。
- T1/T5 代码完成：系统提示词（自称 + 始终简体中文）、启动问候、停止命令"已停止。"、Windows 通知；web.py 3 处中文化。
- HB-014（OpenAI stream 死连接无限阻塞）：`_iter_stream_with_timeout`(120s) + `_MAX_TOOL_LOOPS` 15→3 + `max_tokens` 512；TTS 未就绪时启动问候崩溃修复（best-effort）。
- T2 训练链：torchinfo/torchmetrics/pandas/matplotlib/scipy1.14.1/numpy2.2.6 等装齐（pip 索引死 → `_dl_wheels.py` urllib+wheel 本地安装模式）；`openWakeWord/generate_samples.py` GSV shim（冒烟 PASS、断点续传、3 次重试）；官方英文 adversarial 生成器 CJK 不可用 → `_t2_train_cn.py`（train.py 副本 + `cn_generate_adversarial_texts` 同音字/部分短语/重叠音节真词池，30 条测试通过）；config UTF-8 读取修复。
- **HB-015**：e2e"无响应"假阴性——根因 = 测试脚本收 response 后未 break（服务端一直正常投递，收包日志证实 37.0s 送达）；测试加 `break` + 逐条收包日志；期间误加的 web.py 直接 send 已撤除（保持广播单路径）。
- **2026-10-14 22:0x e2e 正式 PASS**：34.7s，自称"爱莉希雅（Elysia）"✓、简体中文 ✓ → T1/T5 完成；全部 DBG 打点清除，py_compile 通过。
- 进行中：T2 `--generate_clips` 后台合成中（pwsh-103，4800 条 ~5h）→ augment → train → config 指向新 onnx + 加载验证；T4 待用户手动操作 GitHub（need_user.md Q5）；T6 仅 todo。

## Git 提交记录

- `7d279a7`（2026-10-13-10:4x，main）`docs(AI): 补全 Jarvis 运行记录并归档 Q1（端到端 CHAT_OK）`——9 files, +273/−2：records/、hard_bug.md、need_user.md（+ai_buckup 归档）、progress/todo/tree、config.yaml、.gitignore。**已本地 commit，未 push。**
- `f444b85`（2026-10-13-12:5x，main）`feat(AI): 新增 gptsovits TTS provider 并关闭 Qwen3 thinking 解决 LLM 挂起`——11 files, +282/−39：jarvis/tts.py（双 provider）、jarvis/main.py（max_tokens+chat_template_kwargs）、config.yaml、.gitignore、records×2、hard_bug.md（HB-007/HB-008）、need_user.md（Q2）、progress/todo/tree。**已本地 commit，未 push。**
- `409cc3f`（2026-10-13-14:5x，main）`docs(AI): sync GPT-SoVITS venv retry, e2e PASS, and user asks`——4 files, +16/−2：records/2026-10-13-11-55（pwsh-50 失败复盘+分批重装计划）、todo.md（e2e PASS 勾选、venv/ffmpeg 项更新）、need_user.md（Q3 停 llama :8080）、progress.md。**已本地 commit，未 push。**
- `f4e1b48`（2026-10-13-18:1x，main）`fix(AI): repair config.yaml escape/encoding, pin chroma embedding to workspace, close Q2/Q3`——18 files, +195/−126：config.yaml（单引号修复+纯 UTF-8）、jarvis 9 文件（open 补 encoding）、memory.py（WorkspaceMiniLM/HB-007）、.gitignore（.chroma-models/）、need_user/hard_bug 解决并归档 ai_buckup/*_2026-10-13-17-45.md、records/progress/tree。**已本地 commit，未 push。**
- `e9b90f0`（2026-10-13-20:1x，main）`fix(AI): gptsovits provider live + GPT-SoVITS runtime patches, TTS verified`——7 files, +66/−7：config.yaml（tts.provider→gptsovits）、删除工作区根多余 `tools/` 包（import shadowing）、hard_bug.md（HB-009/010/011 已解决）、need_user.md（Q4 待用户重启 llama）、records/progress/todo 同步。**已本地 commit，未 push。**
- `6b1b545`（2026-10-13-21:3x，main）`fix(AI): merge memory facts into single system message; UTF-8 console hardening`——9 files, +258/−31：jarvis/main.py（HB-012 stdout/stderr utf-8 reconfigure、HB-013 facts 合并进单条 system、`_strip_think` 清残留 ⌵/⌖）、hard_bug.md（HB-012/HB-013 已解决）、need_user.md（Q4 done）+ 归档 `ai_buckup/need_user.md_2026-10-13-21-12-19.md`、`_chat_template.jinja`（HB-013 根因参考：GGUF 内 Qwen3.8 chat template）、records/progress/todo/tree 同步。**已本地 commit，未 push。**
