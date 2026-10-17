# 总设计

- **版本**：v1.0（首次创建，无旧版归档）
- **更新时间**：2026-10-17-17-2x
- **关联需求**：records/2026-10-17-17-16-41.md（T7 操作记录 + SQLite / T8 固定应答词 wav / T9 start_all.bat）

> 用户要求"先记入 design 再开工"。本文件为总设计，后续影响设计的新需求将归档旧版至 `ai_buckup/design.md_时间.md` 并递增版本。

## 背景

JarvisAi（爱莉希雅）：openWakeWord 唤醒（v0.3c ONNX @ 阈值 0.7）→ faster-whisper STT → llama.cpp/Qwen LLM → GPT-SoVITS TTS；Web UI（FastAPI + WS，:7860）目前只有实时事件推送、无任何持久化记录，且唤醒应答词"嗯？我在听。"每次走实时 SoVITS 合成（CPU ~数秒），响应慢。

## T7 操作记录 + SQLite 持久化 + Web UI 展示

### 数据模型
- 新模块 `jarvis/events.py`（跟随 `memory.py` 的 sqlite 模式：sqlalchemy engine，短事务）。
- 数据库：`jarvis/data/events.db`（复用已有 `jarvis/data/` 目录，与 `memory.db` 并列；WAL 模式）。
- 表：
  ```sql
  CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,        -- 本地 ISO 时间 yyyy-MM-dd HH:MM:SS
    kind TEXT NOT NULL,      -- wake | user | assistant | system
    text TEXT,               -- 内容（wake/system 可为描述句）
    source TEXT             -- voice | web | startup | error
  );
  ```
- API：`EventLog.log(kind, text, source)`（同步、线程安全，失败仅打印不抛）；`EventLog.recent(limit)`。

### 写入点（main.py）
| 时机 | kind | source |
| --- | --- | --- |
| `_handle_wake_inner` 唤醒检测成功（立即，先于 STT） | wake | voice |
| 转写成功 | user | voice/web |
| 转写为空（"没听清"分支） | system | voice |
| 语音停止命令 | system | voice |
| `_process_request` 收到文本 | user | voice/web |
| `_process_request` 得到回复 | assistant | voice/web |
| `handle_wake` 异常兜底 / 启动问候 | system | startup/error |

→ 满足 a（唤醒即有记录）与 b（不依赖网页端，全部走 sqlite）。

### Web 读取 + UI
- `web.py` 新增 `GET /api/events?limit=100`：返回最近 N 条（旧→新）JSON。
- `static/index.html`（最小改动，不做整体改版——UI 爱莉希雅化 T6 仍延后）：
  - 页面加载 / WS 连接成功后 `fetch('/api/events')` → user/assistant 行渲染进 chat 区（带 voice/web 徽标），wake/system 行渲染进 Live 面板；
  - 新增 WS 事件类型 `wake`（服务端在唤醒检测时广播）→ Live 面板即时追加一行 `🎤 WAKE`；
  - Live 面板空态文案由 "LIVE FEED STANDBY" 改为 "RECORDS STANDBY"（体现记录语义）。

### 验收
1. 仅启动进程（不开网页）触发唤醒 → `events.db` 出现 wake 行；
2. 网页打开 → Live/chat 区可见历史记录；新事件实时追加；
3. `/api/events` 返回正确 JSON（curl 验证）。

## T8 固定应答词 wav

### 数据
- 备选 5 句：`嗯？我在听。` / `你说，我在听。` / `哎，我在呢。` / `嗯，请讲。` / `我在听，你说吧。`
- 预合成脚本 `_gen_ack_wavs.py`（`_*.py` 模式，不入库）：逐句调 GSV api_v2（:9880，爱莉希雅参考音配置同 config.yaml tts.gptsovits）→ `jarvis/data/ack/ack_01.wav` … `ack_05.wav`（24kHz int16 wav，soundfile/wave 校验时长 > 0）。
- `config.yaml` 新增：
  ```yaml
  tts:
    ack_dir: jarvis/data/ack
    ack_phrases: [...]   # 与预合成文件一一对应（供重新生成）
  ```

### 运行路径
- `tts.py` 新增 `play_ack_wav() -> None`：从 `ack_dir` 随机取一个 wav → wave 读取 → `sd.play` 播放（与 `speak()` 同机制：可被 `stop_speaking()` 打断，`_speaking` 事件置位）；目录不存在/为空 → 回退 `speak("嗯？我在听。")`（实时 TTS，保持健壮）。
- `main.py` `_handle_wake_inner`：`_speak_if_unmuted("嗯？我在听。")` → 未静音时 `play_ack_wav()`。

### 验收
1. 5 个 wav 存在且时长 > 1s（脚本校验输出）；
2. 唤醒应答播放耗时 < 1s（本地文件读取+播放，无 HTTP 合成）——日志打点前后时间戳对比；
3. 删空 ack 目录时回退实时 TTS 不崩（代码路径检查 + 冒烟）。

## T9 start_all.bat

- 位置：仓库根 `start_all.bat`（UTF-8 with BOM / chcp 65001，中文注释不乱码）。
- 行为：
  1. `chcp 65001 >nul`；`cd /d %~dp0`（锚定仓库根，任意位置双击可运行）；
  2. **GSV 窗口**：`start "GPT-SoVITS" cmd /k` → `cd GPT-SoVITS-main && ..\.venv-gsv\Scripts\python.exe -X utf8 api_v2.py`（:9880）；
  3. **Jarvis 窗口**：`start "AiliXiya" cmd /k` → 设 `HF_ENDPOINT=https://hf-mirror.com`（HB-029：必须带 scheme）、`HF_HOME=<仓库根>\.hf-cache`、`HF_HUB_DISABLE_XET=1`，然后 `..\.venv\Scripts\python.exe -u -m jarvis.main`（:7860）；
  4. 主窗口 echo 启动清单 + 提示：llama.cpp 由用户自行启动（need_user Q1），爱莉希雅 :7860 自动开浏览器。
- 不纳入 llama.cpp；不杀已存在进程（重复运行会产生重复端口，echo 中提示"若端口被占用请先关旧窗口"）。

### 验收
1. 文件存在、语法可解析（`cmd /c start_all.bat` 干跑会真起服务 → 仅做静态检查：路径/命令存在性校验 + 人工审阅；不重复起服务）；
2. 各引用文件（venv python、api_v2.py、jarvis.main）实际存在。

## 约束与风险

- 服务跨会话间隙会死：验证前先探 :9880/:7860；
- HF env 必须带 `https://` scheme（HB-029）；
- 不 push、不远程写入；本地 commit；
- 唤醒误触率 9% @0.7（v0.3c），T8 加速后若误触感更明显，可微调 threshold（已有结论在 records/2026-10-13-21-38-01.md）。
