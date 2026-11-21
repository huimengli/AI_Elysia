# 轮 5 · 看门狗（HB-049）

- 时间：2026-11-21 11:11:42
- 场景：真 jarvis 在看门狗下起，25 s 后由 watchdog 杀（补 USERPROFILE/MPLCONFIGDIR/HF_* 后）
- 期望：退出码落盘 + 日志尾有 jarvis 行 + killed=True + clean_exit 标记不在
- 实际：{"tag": "wdtest5", "pid": 17992, "exit_code": 259, "killed_by_watchdog": true, "end": {"wall": "2026-11-21 11:11:42", "mono": 53341.218}, "alive_s": 25.5, "clean_exit_marker": false, "log_tail": ["  File \"<frozen runpy>\", line 198, in _run_module_as_main", "  File \"<frozen runpy>\", line 88, in _
- 结果：**PASS**
- 备注：空 env 时 Path.home() 崩（tts.py:33）；补 env 后 jarvis 起得来

证据文件：`.tmp/wdtest5.start` / `.exit` / `.log`（被 .gitignore 忽略，本地可查）。
跑法：`.venv\Scripts\python.exe .tmp\watchdog_test.py`（轮 1-4）与 `.tmp\watchdog_test2.py`（轮 5-6 补 env）。
