# Tree — 结构快照（仅非 .gitignore 文件）

更新时间: 2026-11-09-21-40（新增 `records/2026-11-09-21-19-29.md` 与 `tests/2026-11-09-21-19-29_cc/`（5 个文件），共 152 项；`start_all.bat` 为本轮改动（ASCII + CRLF + `start` 四窗口）。本文件由 `git ls-files` + 未跟踪的非忽略文件（2 项）+ 本轮新增重建；`.tmp/` 被 `.gitignore` 排除，不列出）

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
│   └── progress.md_2026-11-09-17-25-00.md
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
│   └── 2026-11-09-21-19-29.md
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
    └── 2026-11-09-21-19-29_cc (opinion.md + record_1..3)
```

注：`start_all.bat` 为编码/窗口改动（2026-11-09-21-19-29）；`jarvis/wake.py`、`jarvis/web.py`、`jarvis/static/index.html` 为唤醒灯改动（2026-11-09-20-35-43）。
