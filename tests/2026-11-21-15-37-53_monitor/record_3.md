# 验证轮 3 — 子进程起、日志接管、关闭授权

时间：2026-11-21 16:23（主体）→ 16:35（追加段），沙箱内 stub 服务（`.tmp/stub_svc.py`：bind 9880 + 打 3 行日志 + 挂着）
场景：把真 llama/GPT-SoVITS 换成 stub 占位（沙箱内起真 llama 要吃 24 GB 提交内存，不划算），走同一条 `launch`/`snapshot`/`stop_service` 路径。
期望（design v3.1 §1/§4/§5）：
1. `launch` 端口空闲 → `status:"launched"` + pid + source「jarvis 起」，pid 进授权名单。
2. 子进程 stdout 逐行进环形缓冲（带时间戳，`\r` 断行）。
3. 快照行有 pid、提交 MB、来源。
4. `stop_service` 对**自起 pid** 真杀，回显 taskkill 真实输出，名单清空。

实际（逐字照实）：
```
轮3 残留名单 {}
轮3 起子进程 {"name": "stub", "status": "launched", "pid": 21928, "source": "jarvis 起"}
轮3 快照 {"name": "stub", "label": "stub :9880", "pid": 21928, "source": "jarvis 起", "mem_mb": 3, "log_lines": 7}
轮3 名单 {"stub": 21928}
轮3 抓到日志 7 [["16:23:57", "stub: 模拟服务已起 port 9880"], ["16:23:57", "stub: line 1（模拟服务日志行）"], … ["16:23:59", "stub: 5 行打完，继续挂着"]]
轮3 关自起pid SUCCESS: The process with PID 16144 (child process of PID 21928) has been terminated. …
轮3 关后名单 {}
轮3 关后服务行 [{"name": "stub", "label": "stub :9880", "pid": null, "source": "未起", "mem_mb": -1, "log_lines": 8}]
```
第 1 遍（16:23 前）崩在快照：`_mem_mb` 用 `ctypes.windll.psapi.K32GetProcessMemoryInfo`，Python 3.12 报 `AttributeError: function not found`（第 104 处自曝，改 kernel32 后 mem_mb=3 才出来）。

结果：**PASS（4/4）**。taskkill 真实输出照抄进日志区（不是「已关闭」这种自造话）；关后 pid 行变「未起」但环形缓冲仍留 8 行（关窗后日志可读，design §4）。
备注：**追加段（16:35，端口已占用 = 外部起）**
```
追加 外部起前端口 True
追加 外部起接入 {"name": "stub", "status": "external", "pid": 22344, "source": "外部起 · 无日志接管"}
追加 快照 来源/pid/日志 外部起 · 无日志接管 22344 0 {}
追加 关外部pid 拒绝：pid 22344 不是本进程起的（名单里只有 ）
追加 关后端口仍在 True
```
外部 pid 22344 与 `netstat -ano` 真值（`TCP 127.0.0.1:9880 … LISTENING 22344`）一致；端口仍占用 = 没被杀（§5「不静默杀外部服务」）。第 106 处自曝：第 1 版 stub 只 print 不 bind，「外部起」这条根本没触发；第 107-111 处自曝：ctypes 查 pid 连踩 4 次，最后改用 `netstat -ano`。
未测（照实）：关窗全关的 CTRL_CLOSE_EVENT（约 5 s 时限）在沙箱不可测；真机 jarvis 起 /monitor 窗口、不最大化、窗口数 ≤3 口径一致 —— 要你在会话里看。
