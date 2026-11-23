# 第 3 轮（正面路径 + 非自起拒绝 + 自起 pid 关闭对照，2026-11-23-12-42）· 真 `dispatch` + 真窗口真 CDP + 收尾

- **时间**：2026-11-23 12:41–12:44（本地）。两次跑：`.tmp/probe_p1_3_r3_2026-11-23.py` + `.tmp/probe_p1_3_r3b_2026-11-23.py`（补状态复读）。
- **场景**：`dispatch open_url` 起 jarvis 自己的监视页窗口 → `dispatch focus_window(自起标题)` → `dispatch focus_window(非自起标题)` → `kill_recorded_pid(你的窗口 pid)` → `dispatch click_page_text(最新追加)` + `browser_cdp.evaluate` 复读面板状态 → `manage_browser_windows(False)` 计数 → `kill_recorded_pid(自起 pid)` 收尾。
- **实际**：
  - `dispatch open_url` → 「已用 chrome.exe 带参数启动 …，并复读到**页面地址证据**…」；`_jarvis_windows() = [(7320, '监视界面 — 爱莉希雅 - Google Chrome')]`（正面路径的窗口证据）。
  - 正面路径：`dispatch focus_window(自起标题)` → **「已聚焦窗口：监视界面 — 爱莉希雅 - Google Chrome（进程 7320）」**（闸放行，因为 pid 在记录里）。
  - 非自起：`dispatch focus_window('Program Manager')`（pid 9172）→ **拒绝、没有执行**；闸后 `FG = (656424, 7320, '监视界面 — 爱莉希雅…')`，前台落在 jarvis 自己的窗口，你的窗口没被聚焦。
  - `kill_recorded_pid(9172)` → **「pid 9172 不在我起的窗口记录里，拒绝关闭。」**（你的窗口永远不是关闭对象）。
  - 正面路径的页面动作：补测里 `evaluate` 复读 **点前「最新追加|状态：最新追加（滚到底，新行落底部）」→ 点后「查看|状态：查看（视野冻结…）」**，`dispatch click_page_text` 真把按钮点了、状态真翻转。
  - `manage_browser_windows(False)` → 「我起的浏览器窗口 **1 个（上限 3，你的窗口不计）**：监视界面 — 爱莉希雅 - Google Chrome。浏览器窗口共 2 个。未关闭任何窗口。」
  - 收尾：`kill_recorded_pid(7320)` → `SUCCESS`，之后 `自起窗口数 = 0`；补测 `kill_recorded_pid(2968)\` → `SUCCESS`。剪贴板逐字相同 True；`FG 末尾 = (262758, 15380, '检查文件污染 — DSH 本地构建 - Google Chrome')`。
- **结果**：**PASS**
- **自曝第 256 处**：我在第 3 轮第一次跑里写 `dispatch('evaluate', …)` 想复读面板状态，返回 **「未知工具：evaluate」**——`evaluate` 不是注册工具名（它是 `browser_cdp` 的函数，不在 `router` 的工具表里）。正面路径的「点了真的有效」这一条靠补测的 `browser_cdp.evaluate` 才成立。教训：测工具要用注册名，测函数要用函数入口，两者不是一回事；把 `未知工具` 当成「点击没生效」就是假结论。
