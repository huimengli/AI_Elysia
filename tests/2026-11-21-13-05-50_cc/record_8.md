# 轮 8 · HB-053 修法①「归属门禁」第 1 轮（验证 3 轮的第 1 轮）

- 时间：2026-11-21 13:52:42
- 场景：门装在 `browser_cdp.targets()`（所有 CDP 动作的入口：`open_cdp` / `evaluate` / `pages` 都经它）与 `desktop.focus_window`。归属口径照 Q29/Q32/Q34：**pid 必须在 `PID_FILE` 记录 + jarvis 专用 profile 里**。
- 期望：页面动作只发生在 jarvis 自起窗口上；**不是你起的窗口一律不动**（返回，不执行）。
- 实际（逐条）：
  - `read_page` → 读不到页面文本（CDP 连不上：CDP 端口 9333 连不上（没有我起的窗口带 --remote-debugging-port））
  - `find_on_page` → 读不到页面（CDP 连不上：CDP 端口 9333 连不上（没有我起的窗口带 --remote-debugging-port））
  - `click_page_text` → 读不到页面（CDP 连不上：CDP 端口 9333 连不上（没有我起的窗口带 --remote-debugging-port））
  - `focus_window` → 找不到标题包含「星之翼」的窗口。
  - `focus_window` → 找到窗口「P2以上项目问题列出 — DSH 本地构建 - Google Chrome」（进程 5244），但它**不是 jarvis 起的窗口**（pid 不在 `.tmp/jarvis_browser_pids.jso
  - `navigate_url` → 我自己起的浏览器窗口 0 个（浏览器窗口共 1 个）。**你的窗口我不聚焦、不输入**，https://www.bilibili.com/ 未打开；要我自己起窗口请用 open_url（上限 3，只数我的窗口）。
- 门禁扫到的 pid 集合大小：45。**更正一条**：我此前记「沙箱里 profile pid 扫不出来、返回 set()」——那条只在 **node spawn（piped stdio 被拒）** 里成立；由 pwsh 起的 python 里进程扫描**能用**，这次扫到 45 个 profile pid。
- 关键证据：`focus_window(DSH)` 返回「找到窗口「P2以上项目问题列出 — DSH 本地构建 - Google Chrome」（进程 5244），但它**不是 jarvis 起的窗口**……**没有执行**」——**这正是轮 21 那条越界的堵法**。
- 窗口清单差异：第 3 行前「2017MFM（进程 6092）」后「艾尔登异环（进程 6092）」——**同一个 pid，标题是它自己改的**（你在玩游戏），pid 6092 全程没被我碰（`focus_window(星之翼)` 返回「找不到」，对 5244 的聚焦被门禁拒）。第 5 行的差异是我把清单截到 110 字造成的显示差。
- 结果：**PASS（门禁生效，没有任何窗口被聚焦/导航）**
- 未测：**正面路径要在你的会话跑**（`start_all` 起 jarvis，我经共用浏览器点「播放音乐」/读页面，验「9333 上确实有我的窗口，且只动它」）。我沙箱里 9333 连不上（我的窗口随驱动进程一起没），所以只验到 **fail-closed 的拒绝路径**。
