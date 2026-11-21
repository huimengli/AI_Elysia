# 轮 2 · 看门狗（HB-049）

- 时间：2026-11-21 11:04:01
- 场景：子进程抛未捕获异常
- 期望：退出码非 0 + 日志尾有 Traceback
- 实际：{"tag": "wdtest2", "pid": 2944, "exit_code": 1, "killed_by_watchdog": false, "end": {"wall": "2026-11-21 11:04:01", "mono": 52880.437}, "alive_s": 0.5, "clean_exit_marker": false, "log_tail": ["Traceback (most recent call last):", "  File \"<string>\", line 2, in <module>", "NameError: name '�����' 
- 结果：**PASS**
- 备注：stdout 重定向到文件（非管道），traceback 落得下来

证据文件：`.tmp/wdtest2.start` / `.exit` / `.log`（被 .gitignore 忽略，本地可查）。
跑法：`.venv\Scripts\python.exe .tmp\watchdog_test.py`（轮 1-4）与 `.tmp\watchdog_test2.py`（轮 5-6 补 env）。
