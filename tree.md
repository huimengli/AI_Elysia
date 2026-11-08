# Tree — 结构快照（仅非 .gitignore 文件）

更新时间: 2026-11-08-20:16（新增 records/2026-11-08-19-52-59.md、tests/2026-11-08-19-52-59_cc/、ai_buckup/progress.md_2026-11-08-20-14.md）

```
JarvisAi/
├── .gitignore
├── AI_Benchmark.md
├── JARVIS_STATE.md
├── LICENSE
├── PROJECT_SUMMARY.txt
├── README.md
├── _chat_template.jinja
├── ai_buckup
│   ├── hard_bug.md_2026-10-13-17-45.md
│   ├── need_user.md_2026-10-13-09-56-54.md
│   ├── need_user.md_2026-10-13-17-45.md
│   ├── need_user.md_2026-10-13-21-12-19.md
│   ├── progress.md_2026-10-15-13-49-00.md
│   ├── progress.md_2026-11-08-12-40-22.md
│   ├── progress.md_2026-11-08-18-48.md
│   └── progress.md_2026-11-08-20-14.md
├── config.yaml
├── design.md
├── dsh-my-presets
│   ├── cordis.patch.yml
│   └── package.json
├── hard_bug.md
├── install.bat
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
├── need_user.md
├── openWakeWord
│   ├── generate_samples.py
│   └── output
│       └── aili_xiya_v0.3
│           └── aili_xiya_v0.3.onnx
├── progress.md
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
│   └── 2026-11-08-19-52-59.md
├── requirements.txt
├── start.bat
├── start_all.bat
├── tests
│   ├── 2026-11-08-14-12-32_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-15-16-18_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   ├── record_3.md
│   │   ├── record_4.md
│   │   ├── record_5.md
│   │   └── record_6.md
│   ├── 2026-11-08-17-29-39_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-17-53-00_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-18-16-33_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-18-39-40_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-18-54-18_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-19-25-48_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── 2026-11-08-19-52-59_cc
│   │   ├── opinion.md
│   │   ├── record_1.md
│   │   ├── record_2.md
│   │   └── record_3.md
│   ├── __init__.py
│   ├── opinion.md
│   ├── test_context.py
│   ├── test_llm.py
│   ├── test_memory.py
│   ├── test_stt.py
│   ├── test_tools.py
│   └── test_tts.py
├── todo.md
└── tree.md
```

