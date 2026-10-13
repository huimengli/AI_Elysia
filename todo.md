# Todo

- [x] 2026-10-12-12-28-30 将 Jarvis 项目运行起来（→ records/2026-10-12-12-28-30.md；2026-10-13-10:3x 端到端 CHAT_OK）
  - [x] 环境检查（Python 3.12 ✓ / Ollama 未装，按用户要求不装）
  - [x] config.yaml：LLM 指向 llama.cpp @ 127.0.0.1:8080/v1
  - [x] config.yaml：wake_word.model 定为内置 `hey_jarvis_v0.1`（原 `jarvis` 与 CWD 目录同名冲突，见 hard_bug.md HB-001）
  - [x] 安装依赖到 .venv（阿里云镜像卡死 torch → 换清华镜像成功；AppData pip 缓存被拒 → PIP_CACHE_DIR 指向工作区 `.pip-cache`）
  - [x] 下载 openWakeWord 模型（9 个 ONNX，含 hey_jarvis_v0.1 / melspectrogram / embedding；GitHub TLS 失败 → Python urllib + 大小校验，加载验证通过 OWW_OK）
  - [x] 预下载 TTS/STT 模型到 `.hf-cache`（Kokoro-82M 72 文件含 kokoro-v1_0.pth 312MB + faster-whisper-small model.bin 461MB；HF_ENDPOINT=hf-mirror.com + HF_HUB_DISABLE_XET=1，见 HB-002）
  - [x] espeak-ng-data 部署到 DLL 硬编码路径 `D:\a\espeakng-loader\...`（364 文件，用户批准越权写入；DLL 忽略参数与 env，根因见会话记录）
  - [x] spacy `en_core_web_sm` 装入 .venv（GitHub 全阻 → HF-mirror `spacy/en_core_web_sm` wheel 3.7.1 改名 `--no-deps` 安装，加载验证 OK，仅兼容性警告）
  - [x] `_tts_test.py` 端到端 TTS 合成通过（TTS_TEST_OK chunks=1；当时 free 已低至 ~400MB，HB-003 风险实证）
  - [x] 启动 `python -m jarvis.main`（后台作业 pwsh-50，HF_HOME 指向工作区 `.hf-cache`），Web UI :7860 HTTP 200 ✓
  - [x] 2026-10-13 机器重启后后台重启 Jarvis（作业 pwsh-2），Web UI :7860 HTTP 200 ✓
  - [x] need_user.md Q1 已答复并归档（用户：llama 由其自行启动，需要时 agent 发请求 → `ai_buckup/need_user.md_2026-10-13-09-56-54.md`）
  - [x] WS 聊天走通 LLM：2026-10-13-10:3x 用户启动 llama.cpp @ :8080（模型与 config 一致，零改动）→ `_ws_chat_test.py` **CHAT_OK** ✓（Qwen 真实回复），HB-004 解除
  - [x] llama.cpp 启动请求已发出并获用户执行（建议 8090 → 实际用户用回 :8080，Steam 已消失）
  - [ ] 收尾：更新 records/progress/tree.md、本地 git commit（不 push；`_ws_chat_test.py` 保留至验证完成）
