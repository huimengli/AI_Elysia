# AI_Elysia — 爱莉希雅 · 本地 AI 语音助手

> 以「爱莉希雅」命名的全本地 agentic AI 语音助手：说 **"爱莉希雅"** 唤醒 → 问任何问题 → 她读屏、操控桌面、搜索网页，并用语音回答。全部组件运行在本机，无需云端。

> **本仓库为自用项目**：fork 自上游项目 [PanPenek/jarvis](https://github.com/PanPenek/jarvis)（原 J.A.R.V.I.S.，MIT 许可），并按本机环境与爱莉希雅语音/人格全面适配。不是通用产品。

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Windows](https://img.shields.io/badge/platform-Windows-0078D6)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Fork 说明

- **上游仓库**：[PanPenek/jarvis](https://github.com/PanPenek/jarvis)（MIT）——提供基础架构：唤醒词 → STT → LLM（31 个内置工具）→ TTS + FastAPI Web UI。
- **本仓库**：`huimengli/AI_Elysia`，自用 fork，保留上游代码与目录约定（records/、tests/、hard_bug.md、progress.md 等台账体系）。
- **本仓库主要改动**（相对上游）：
  - 唤醒词：自训练 openWakeWord v0.3，短语 **"爱莉希雅"**（recall 0.94 / 误触 0.09 @ 阈值 0.7）；不再使用原 "Hey Jarvis"。
  - TTS：Kokoro → **GPT-SoVITS 2.0 爱莉希雅音色**（见下文「权重来源」）；5 条预合成唤醒应答 wav，唤醒时随机本地播放。
  - LLM 默认 provider：**llama.cpp**（`Qwen3.8-27B` GGUF，`http://127.0.0.1:8080/v1`，用户自启）；Ollama 保留为备选。
  - 一键启动：`start_all.bat`（GSV :9880 + Jarvis :7860，含 HuggingFace 镜像 env）。
  - 事件日志：新增 `jarvis/events.py` → `jarvis/data/events.db`（SQLite/WAL），wake/user/assistant/system 即时落库（不依赖网页端）；`GET /api/events?limit=N`；Web UI 加载历史记录 + WS 实时追加。
  - Web UI 仍为上游 HUD 风格，爱莉希雅化尚未做（见 todo.md）。

## 语音与模型权重来源

**除唤醒词模型（自训练，随本仓库提供）外，其余权重均不包含在本仓库内**（`.gitignore` 排除）。首次启动前请确认「用户提供」类型的文件已就位到对应路径；「自动下载」类型会在首次运行时经 HF 镜像自动拉取。

| 权重 | 类型 | 来源说明 | 位置 |
| --- | --- | --- | --- |
| TTS 音色（SoVITS） | 用户提供 | `[GPT2.0] Elysia` 模型包：`Elysia_e16_s8720.pth` / `Elysia_e20_s10900.pth` / `Elysia_e24_s13080.pth` | `GPT-SoVITS-main/SoVITS_weights_v2/` |
| TTS 音色（GPT） | 用户提供 | 同模型包：`Elysia-e5/e10/e15/e20.ckpt` | `GPT-SoVITS-main/GPT_weights_v2/` |
| 参考音频 | 用户提供 | `【感动】欸嘿，大家笑一笑，好吗？`（见 `config.yaml` → `tts.gptsovits.ref_audio_path`） | `F:\BaiduNetdiskDownload\爱莉希雅\【GPT-SoVITS 2.0】爱莉希雅\参考音频\` |
| 唤醒词模型 | 自训练（已入库） | openWakeWord v0.3（`aili_xiya_v0.3.onnx`，recall 0.94 / 误触 0.09 @ 0.7；仅该 onnx 入库，训练 wav 等仍被忽略） | `openWakeWord/output/aili_xiya_v0.3/`（随仓库提供） |
| LLM 权重 | 用户提供 | 魔搭社区 `Qwen3.8-27B` GGUF 量化（见 `config.yaml` → `llm.providers.llamacpp.model`） | `F:\魔搭社区\Qwen3.8-27B-Q4_K_M-GGUF\` |
| STT 模型 | 自动下载 | faster-whisper `small`（int8，首次运行经 HF 镜像下载） | `.hf-cache/` |

## 快速开始

### 前置条件

- **Windows 10/11**
- **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/)
- **llama.cpp**（在 `:8080` 提供 `Qwen3.8-27B` GGUF，用户自启）或 **Ollama** — [ollama.com/download](https://ollama.com/download)

### 1. 安装

```bat
git clone https://github.com/huimengli/AI_Elysia.git
cd AI_Elysia
install.bat
```

创建 Python 虚拟环境（`.venv`）、安装全部依赖；唤醒词 ONNX 若本地不存在会尝试下载。

> ⚠️ GSV 语音包、参考音频、唤醒词模型、LLM 权重**均不在本仓库内**，位置与类型见上表「权重来源」。首次启动前请确认这些文件已就位。

### 2. 一键启动

```bat
start_all.bat
```

弹出两个独立窗口：

- **GPT-SoVITS** `http://127.0.0.1:9880`（语音合成，使用 `.venv-gsv`）
- **Jarvis** `http://127.0.0.1:7860`（主程序 + Web UI，已带 HuggingFace 镜像 env）

llama.cpp `:8080` 不纳入本脚本，使用前请自行启动。

### 3. 使用

| 方式 | 操作 |
| --- | --- |
| **语音** | 说 **"爱莉希雅"** → 等应答词（本地 wav）播完 → 说出指令 |
| **Web UI** | 打开 http://localhost:7860，底部聊天栏输入 → 点发送（历史记录自动加载） |
| **键盘** | 按 **F2** → 终端输入指令 → Enter |

---

## 架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Wake Word  │────▶│    STT       │────▶│     LLM      │
│(openWakeWord)│    │(faster-whisper)│   │(llama.cpp/API)│
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
┌─────────────┐     ┌──────────────┐     ┌──────▼───────┐
│   Web UI    │◀───▶│  Event Bus   │◀────│  Tool Router │
│ (FastAPI)   │     │ (WebSocket)  │     │ (31 tools)   │
└─────────────┘     └──────┬───────┘     └──────┬───────┘
                           │                    │
                     ┌─────▼──────┐       ┌─────▼──────┐
                     │  Memory    │       │    TTS     │
                     │(SQLite+    │       │(GPT-SoVITS │
                     │ ChromaDB)  │       │ 爱莉希雅音色)│
                     └────────────┘       └────────────┘
```

**管线：** 唤醒词（爱莉希雅）→ 播放本地应答 wav → 录音至静音 → 转写（faster-whisper）→ LLM + 工具（最多 15 步链式调用）→ GPT-SoVITS 爱莉希雅音色语音播报；每步同步写入 `jarvis/data/events.db`。

**全部组件本地化。** 除非自行配置云端 LLM provider，数据不离开本机。

## 事件日志（本仓库新增）

- `jarvis/events.py` → SQLite `jarvis/data/events.db`（WAL），字段 `id, ts, kind, text, source`。
- `kind`：wake / user / assistant / system；`source`：voice / web / startup / error。
- **唤醒即落库**：触发瞬间写入，即使浏览器从未打开。
- API：`GET http://localhost:7860/api/events?limit=50`；Web UI 连接时自动加载历史，WebSocket 实时追加。

## 配置说明（config.yaml）

| 字段 | 说明 |
| --- | --- |
| `wake_word.model` / `threshold` | 唤醒词 ONNX 路径 / 触发阈值（当前 0.7，误触率 ~0.09；如需更稳可上调至 0.72–0.75） |
| `stt.model` / `device` | faster-whisper 模型与设备（本机 CUDA 驱动受限，实际自动降级 CPU/int8） |
| `llm.active_provider` | 当前 LLM provider（默认 `llamacpp`） |
| `tts.provider` / `ack_dir` / `ack_phrases` | GSV API 地址、预合成应答 wav 目录与短语表 |
| `memory.*` | 长期记忆 SQLite + ChromaDB |

## 故障排查

| 现象 | 处理 |
| --- | --- |
| 唤醒时系统卡顿 / 进程崩溃 | RAM 不足：GSV（~3.2 GB）与 LLM 同时驻留，先关闭大内存程序（详见 hard_bug.md HB-003 系）。 |
| STT 报 mkl OOM | 环境性内存压力，释放内存后重试。 |
| HF 模型下载失败 | 确认 `HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME`、`HF_HUB_DISABLE_XET=1` 三个 env（start_all.bat 已带）。 |
| 端口被占用 | 7860 Jarvis / 9880 GSV / 8080 llama.cpp；start_all.bat 会先检查占用，冲突时拒绝启动。 |
| Web UI 不刷新 | 浏览器控制台（F12）查看 `[WS]` 日志，刷新页面。 |

---

## 技术栈

| 组件 | 技术 |
| --- | --- |
| Wake Word | [openWakeWord](https://github.com/dscripka/openWakeWord)（ONNX，自训练 v0.3） |
| Speech-to-Text | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) |
| Text-to-Speech | [GPT-SoVITS 2.0](https://github.com/RVC-Boss/GPT-SoVITS)（爱莉希雅音色，本机 :9880） |
| LLM | [llama.cpp](https://github.com/ggml-org/llama.cpp) / Ollama / OpenAI 兼容 API |
| Memory | SQLite + [ChromaDB](https://www.trychroma.com/) |
| Web UI | [FastAPI](https://fastapi.tiangolo.com/) + WebSocket |
| Desktop Control | [PyAutoGUI](https://pyautogui.readthedocs.io/) + PowerShell OCR |

---

## 许可证

MIT — 见 [LICENSE](LICENSE)。

本仓库 fork 自 MIT 许可的上游项目 [PanPenek/jarvis](https://github.com/PanPenek/jarvis)，按 MIT 条款保留该许可。本仓库为自用；语音音色为用户提供的模型包，不构成本仓库代码的一部分。
