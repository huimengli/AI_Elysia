# 轮 3 · 看门狗（HB-049）

- 时间：2026-11-21 11:04:02
- 场景：子进程 os._exit(7)
- 期望：退出码 7
- 实际：{"tag": "wdtest3", "pid": 18808, "exit_code": 7, "killed_by_watchdog": false, "end": {"wall": "2026-11-21 11:04:02", "mono": 52881.046}, "alive_s": 0.5, "clean_exit_marker": false, "log_tail": []}
- 结果：**PASS**
- 备注：os._exit 不跑 atexit

证据文件：`.tmp/wdtest3.start` / `.exit` / `.log`（被 .gitignore 忽略，本地可查）。
跑法：`.venv\Scripts\python.exe .tmp\watchdog_test.py`（轮 1-4）与 `.tmp\watchdog_test2.py`（轮 5-6 补 env）。
