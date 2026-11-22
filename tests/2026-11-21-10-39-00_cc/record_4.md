# 轮 4 · 看门狗（HB-049）

- 时间：2026-11-21 11:04:06
- 场景：子进程 sleep(60)，watchdog --timeout 3
- 期望：killed_by_watchdog=True + 落码
- 实际：{"tag": "wdtest4", "pid": 13856, "exit_code": 259, "killed_by_watchdog": true, "end": {"wall": "2026-11-21 11:04:06", "mono": 52885.203}, "alive_s": 4.0, "clean_exit_marker": false, "log_tail": []}
- 结果：**PASS**
- 备注：TerminateProcess 后的码记，不美化

证据文件：`.tmp/wdtest4.start` / `.exit` / `.log`（被 .gitignore 忽略，本地可查）。
跑法：`.venv\Scripts\python.exe .tmp\watchdog_test.py`（轮 1-4）与 `.tmp\watchdog_test2.py`（轮 5-6 补 env）。
