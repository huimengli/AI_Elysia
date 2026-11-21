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

## 追加段 2（2026-11-21 17:48-18:15 · 你发来的真会话截图与根因追查）
时间: 2026-11-21-17-48-25 起（你发截图 1446x1034）场景: 你在真会话里开了 `http://127.0.0.1:7860/monitor`（jarvis 自起窗口，带 `--no-sandbox` 警告横幅）期望: 页面渲染出资源条/四灯/服务表/F 块/E 块与日志区实际（截图照实）: 只有静态骨架 ——「读取中…」「四灯：—」、两张表只有表头、日志区 0 个面板；「推送间隔」标签与下拉重叠成「推送间同▼▼ s」。根因（不猜，逐步坐实）: 浏览器解析器把脚本塞进新 `<script>` 后报 `行30:127`：`"<span class=\"ext">无关闭按钮…` 只转义了开引号，`ext` 后的 `"` 把 JS 字符串提前闭合 → 整段 script 语法错 → `ws` 为 undef，页面永停在初始态。第 79 行同坑。修 2 处转义。复测（共用浏览器开同页，真会话 jarvis 在跑）: `ws.readyState 1`、无语法错；`/api/monitor` 数据真：`jarvis 起 pid 8440/1516`、`提交MB 1060/3`、`log_lines 13/19`、`jarvis_windows 1`、四灯 wake/asr/llm/tts 全 online；页面渲染出资源条（提交 24398·已用 20584·可用 3814·物理 30%·CPU 14.1%）、四灯 4 盏 + 我起窗口 1/3、服务表 3 行带「关闭」按钮、F 块 `wake 0.75 · ASR 0.03 s · LLM — s · TTS — s` 与曲线柱、日志区 2 面板（llama 17:47:46 listening/model loaded 2760k tps；tts 17:40:11 WebRTC 警告）→ 见 [C:\Users\楼听\Downloads\monitor_after.png](C:\Users\楼听\Downloads\monitor_after.png)。真机节拍（设 1 s，量 29 拍）: 中位 1.9 s ｜ 均值 1.8 s ｜ 最小 1.4 ｜ 最大 2.0。一次快照实测 1998 ms。逐段计时坐实瓶颈：`jarvis_windows` 1688 ms（`app_control` 首建 243 项索引 + 枚举窗口），`os_stats` 0 ms、`netstat` 冷 67 ms。优化：`netstat` 缓存 TTL 2 s（并删掉「端口缺位就重扫」的错误条件）、窗口计数缓存 TTL 5 s、探针 TTL 1 s。稳态实测：第 2 拍 50 ms、第 3 拍 0 ms。推送「一阵就停」坐实与修: `_monitor_loop` 在 `send_text` 抛异常时把客户端 pop 出 `_mon_state`，而页面只在 open/改间隔发 `monitor_config` → 一次瞬时失败后页面永久静默。修：仅 `ws.client_state == 2`（真断开）才摘；前端加 10 s 心跳重注册。排版: 加 `select{width:58px;margin:0 8px}` 与标签「推送间隔（秒）」，消除重叠。结果: PASS（骨架→真数据，根因 2 处转义）；节拍 1 s 达标 **未测**（要重启 jarvis 才生效）。备注: `--no-sandbox` 横幅照实记（jarvis 起浏览器窗口的命令行标记），未改；要不要去掉要你定。本段自曝第 113-127 处（共 15 处，逐条见 progress）。