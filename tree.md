# Tree — 结构快照（仅非 .gitignore 文件）

更新时间: 2026-11-11-21-15（新增 `tests/2026-11-11-20-34-04_cc/`（opinion.md + record_1..6），`git ls-files --cached --others --exclude-standard` 计 **195 个非忽略文件**（树内按目录折叠展示）；本批**改动 `jarvis/tts.py`（TTS 按中文标点切句 + 合成队列 `speak_queued`，首声 14.1 s→2.4 s）与 `jarvis/stt.py`（ASR 引擎开关 `stt.engine` = whisper/sherpa + `_get_sherpa`/`_sherpa_transcribe`）**；`config.yaml` **未改**（按 Q12 保持 `aili_xiya_v0.6.onnx` + 阈值 0.7）。新增的 `openWakeWord/train_config_v07.yaml`、`train_config_v08.yaml`、`.tmp/_t2_v07_clips.py`、`.tmp/_t2_v07_features.py`、`.tmp/_t2_v08_features.py`、`.tmp/probe_v07_deploy.py` 与 `openWakeWord/output/aili_xiya_v0.7|v0.8/` 均被 `.gitignore`（`openWakeWord/*`、`_*.py`、`.tmp/`、`*.wav`）排除，不列出。旧版已归档 `ai_buckup/tree.md_2026-11-11-21-15-00.md`。上一版（2026-11-11-19-59）新增 `records/2026-11-11-19-45-46.md` 与 `tests/2026-11-11-19-45-46_cc/`（5 个文件），共 193 项；本批**改动 `config.yaml`**：`wake_word.model` 由 `aili_xiya_v0.3.onnx` 切到 **`aili_xiya_v0.6.onnx`**，`threshold` 保持 0.7、`chunk_size` 1280，Jarvis 已带 3 个 HF 变量重启（health 实测生效）。上一批（2026-11-10-22-48-24）为 commit 标题改中文，无代码/配置改动。本文件由 `git ls-files` + 未跟踪的非忽略文件（2 项）+ 本轮新增重建；`.tmp/` 被 `.gitignore` 排除，不列出；`_t2_v04_real_clips.py`、`_t2_v04_features.py`、`_t2_v04_noisy_clips.py`、`_t2_v05_features.py`、`_t2_v06_clips.py`、`_t2_v06_noisy_clips.py`、`_t2_v06_features.py` 与 `openWakeWord/train_config_v04|v05|v06.yaml`、`openWakeWord/output/aili_xiya_v0.4|v0.5|v0.6/` 均被 `.gitignore`（`_*.py`、`openWakeWord/*`、`*.wav`）排除，不列出）

```
JarvisAi/
├── .gitignore
├── AI_Benchmark.md
├── JARVIS_STATE.md
├── LICENSE
├── PROJECT_SUMMARY.txt
├── README.md
├── _chat_template.jinja
├── config.yaml
├── design.md
├── hard_bug.md
├── install.bat
├── jarvis_screen.png          (未跟踪，非 .gitignore)
├── love_silvia.txt            (未跟踪，非 .gitignore)
├── need_user.md
├── progress.md
├── requirements.txt
├── start.bat
├── start_all.bat              (本次修改：ASCII + CRLF + start 开 4 个 cmd 窗口)
├── todo.md
├── tree.md
├── ai_buckup
│   ├── hard_bug.md_2026-10-13-17-45.md
│   ├── need_user.md_2026-10-13-09-56-54.md
│   ├── need_user.md_2026-10-13-17-45.md
│   ├── need_user.md_2026-10-13-21-12-19.md
│   ├── progress.md_2026-10-15-13-49-00.md
│   ├── progress.md_2026-11-08-12-40-22.md
│   ├── progress.md_2026-11-08-18-48.md
│   ├── progress.md_2026-11-08-20-14.md
│   ├── progress.md_2026-11-09-17-25-00.md
│   ├── progress.md_2026-11-10-21-50-17.md
│   ├── progress.md_2026-11-10-23-00-30.md
│   └── todo.md_2026-11-10-21-52-25.md
├── dsh-my-presets
│   ├── cordis.patch.yml
│   └── package.json
├── jarvis
│   ├── __init__.py
│   ├── context.py
│   ├── events.py
│   ├── llm.py
│   ├── main.py
│   ├── memory.py
│   ├── static
│   │   └── index.html
│   ├── stt.py
│   ├── tools
│   │   ├── __init__.py
│   │   ├── app_control.py
│   │   ├── code_exec.py
│   │   ├── desktop.py
│   │   ├── file_ops.py
│   │   ├── router.py
│   │   ├── subagent.py
│   │   ├── system.py
│   │   └── web_search.py
│   ├── tts.py
│   ├── wake.py
│   └── web.py
├── llm
│   ├── startLlama.ps1
│   ├── startLlamaCpu.ps1
│   └── startLlamaVulkanTest.ps1
├── openWakeWord
│   ├── generate_samples.py
│   └── output
│       └── aili_xiya_v0.3
│           └── aili_xiya_v0.3.onnx
├── records
│   ├── 2026-10-12-12-28-30.md
│   ├── 2026-10-13-11-45.md
│   ├── 2026-10-13-11-55.md
│   ├── 2026-10-13-21-38-01.md
│   ├── 2026-10-14-22-23-49.md
│   ├── 2026-10-15-21-05-48.md
│   ├── 2026-10-17-17-16-41.md
│   ├── 2026-10-17-19-11-07.md
│   ├── 2026-10-17-19-52-00.md
│   ├── 2026-11-08-12-08-49.md
│   ├── 2026-11-08-12-19-15.md
│   ├── 2026-11-08-12-29-18.md
│   ├── 2026-11-08-12-40-22.md
│   ├── 2026-11-08-12-51-25.md
│   ├── 2026-11-08-13-04-48.md
│   ├── 2026-11-08-13-29-56.md
│   ├── 2026-11-08-14-12-32.md
│   ├── 2026-11-08-15-16-18.md
│   ├── 2026-11-08-17-29-39.md
│   ├── 2026-11-08-17-53-00.md
│   ├── 2026-11-08-18-16-33.md
│   ├── 2026-11-08-18-39-40.md
│   ├── 2026-11-08-18-54-18.md
│   ├── 2026-11-08-19-25-48.md
│   ├── 2026-11-08-19-52-59.md
│   ├── 2026-11-08-20-22-00.md
│   ├── 2026-11-08-20-44-17.md
│   ├── 2026-11-09-15-37-58.md
│   ├── 2026-11-09-19-45-46.md
│   ├── 2026-11-09-20-35-43.md
│   ├── 2026-11-09-21-19-29.md
│   ├── 2026-11-09-21-55-14.md
│   ├── 2026-11-10-17-31-10.md
│   ├── 2026-11-10-17-43-08.md
│   ├── 2026-11-10-21-02-16.md
│   ├── 2026-11-10-22-17-39.md
│   ├── 2026-11-10-22-48-24.md
│   └── 2026-11-11-19-45-46.md
└── tests
    ├── __init__.py
    ├── opinion.md
    ├── test_context.py
    ├── test_llm.py
    ├── test_memory.py
    ├── test_stt.py
    ├── test_tools.py
    ├── test_tts.py
    ├── 2026-11-08-14-12-32_cc (opinion.md + record_1..3)
    ├── 2026-11-08-15-16-18_cc (opinion.md + record_1..6)
    ├── 2026-11-08-17-29-39_cc (opinion.md + record_1..3)
    ├── 2026-11-08-17-53-00_cc (opinion.md + record_1..3)
    ├── 2026-11-08-18-16-33_cc (opinion.md + record_1..3)
    ├── 2026-11-08-18-39-40_cc (opinion.md + record_1..3)
    ├── 2026-11-08-18-54-18_cc (opinion.md + record_1..3)
    ├── 2026-11-08-19-25-48_cc (opinion.md + record_1..3)
    ├── 2026-11-08-19-52-59_cc (opinion.md + record_1..3)
    ├── 2026-11-08-20-22-00_cc (opinion.md + record_1..3)
    ├── 2026-11-09-15-37-58_cc (opinion.md + record_1..3)
    ├── 2026-11-09-20-35-43_cc (opinion.md + record_1..3)
    ├── 2026-11-09-21-19-29_cc (opinion.md + record_1..3)
    ├── 2026-11-09-21-55-14_cc (opinion.md + record_1..4)
    ├── 2026-11-10-17-31-10_cc (opinion.md + record_1..3)
    ├── 2026-11-10-17-43-08_cc (opinion.md + record_1..3)
    ├── 2026-11-10-21-02-16_cc (opinion.md + record_1..3)
    ├── 2026-11-10-22-17-39_cc (opinion.md + record_1..3)
    ├── 2026-11-11-19-45-46_cc (opinion.md + record_1..3)
    └── 2026-11-11-20-34-04_cc (opinion.md + record_1..6)
```

注：本轮（2026-11-10-21-02-16）改动 `config.yaml`（`stt.no_speech_seconds: 2.0`）、`jarvis/stt.py`（`record_until_silence` 无人说话 2 s 提前退出）、`jarvis/main.py`（把该参数从配置传入）；唤醒词重训练的新脚本与 `aili_xiya_v0.4/v0.5` 数据被 `.gitignore` 排除，不入库。上一轮（2026-11-10-17-43-08）改动 `config.yaml`、`jarvis/stt.py`、`jarvis/main.py`、`jarvis/tools/{desktop,system,app_control,web_search,file_ops,code_exec,subagent,router}.py`（工具结果文案汉化 + 录音落盘 + ASR 参数）；`jarvis/main.py` 的 whisper 预热属 2026-11-10-17-31-10；`jarvis/tts.py`、`jarvis/tools/router.py`、`jarvis/static/index.html` 为 2026-11-09-21-55-14 改动。
