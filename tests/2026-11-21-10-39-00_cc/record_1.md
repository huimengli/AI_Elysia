# 轮 1 · 看门狗（HB-049）

- 时间：2026-11-21 11:04:01
- 场景：子进程 sys.exit(0)，没挂 clean_exit 钩子（纯码 0）
- 期望：退出码 0；标记不在；判读=不是正常收尾
- 实际：{"tag": "wdtest1", "pid": 1200, "exit_code": 0, "killed_by_watchdog": false, "end": {"wall": "2026-11-21 11:04:01", "mono": 52879.812}, "alive_s": 0.5, "clean_exit_marker": false, "log_tail": []}
- 结果：**PASS**
- 备注：判读照 watchdog 的 verdict 定义

证据文件：`.tmp/wdtest1.start` / `.exit` / `.log`（被 .gitignore 忽略，本地可查）。
跑法：`.venv\Scripts\python.exe .tmp\watchdog_test.py`（轮 1-4）与 `.tmp\watchdog_test2.py`（轮 5-6 补 env）。
