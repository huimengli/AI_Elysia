# 轮 6 · 看门狗（HB-049）

- 时间：2026-11-21 11:11:49
- 场景：register_clean_exit_hook + sys.exit(0)（atexit 跑到）
- 期望：码 0 + .tmp/wdtest6.clean_exit 存在 = 正常收尾判据成立
- 实际：{"tag": "wdtest6", "pid": 17736, "exit_code": 0, "killed_by_watchdog": false, "end": {"wall": "2026-11-21 11:11:49", "mono": 53347.984}, "alive_s": 6.5, "clean_exit_marker": true, "log_tail": ["Traceback (most recent call last):", "  File \"<string>\", line 5, in <module>", "  File \"F:\\git\\Jarvis
- 结果：**PASS**
- 备注：jarvis 真正常收尾（真人会话的收尾路径）照旧未测

证据文件：`.tmp/wdtest6.start` / `.exit` / `.log`（被 .gitignore 忽略，本地可查）。
跑法：`.venv\Scripts\python.exe .tmp\watchdog_test.py`（轮 1-4）与 `.tmp\watchdog_test2.py`（轮 5-6 补 env）。
