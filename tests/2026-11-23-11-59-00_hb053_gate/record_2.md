# 第 2 轮（真 `dispatch` 路径的 7 项空串拒绝 + 窗口/剪贴板逐字对照，2026-11-23-12-37）· HB-053 修法②

- **时间**：2026-11-23 12:36–12:39（本地）。`.tmp/probe_p1_3_r2_2026-11-23.py`，走 `router.dispatch\`（模型同一入口），不是直调工具函数。
- **场景**：7 项带空串 `dispatch\`；再拿真存在的非自起窗口 `Program Manager`（pid 9172）`dispatch focus_window\`；逐字对照 `_visible_windows()\` 窗口集合与 `Get-Clipboard -Raw\`。
- **期望**：7 项全部「拒绝、没执行」（修法②`_WILDCARD_EMPTY\`：`focus_window.title` / `find_on_page.text` / `click_page_text.text` / `find_on_screen.text` / `web_search.query` / `set_clipboard.text` / `show_notification.title+message`）；非自起窗口聚焦被拒；窗口集合与剪贴板逐字不变。
- **实际**：
  - `focus_window / find_on_page / click_page_text / find_on_screen / web_search / set_clipboard / show_notification` 7 项**全部返回拒绝文案**，逐字含「空参数 … 是**通配或真实副作用**（空标题 = 匹配任意窗口；空文本 = indexOf("") 命中第一个元素；空 query = 开一个空搜索页；空文本 = 清空剪贴板），**没有执行**」。
  - `dispatch focus_window('Program Manager')` → 「找到窗口…（进程 9172），但它**不是 jarvis 起的窗口**…**没有执行**。要动它需要你明确授权。」
  - `FG 前 = (262758, 15380, '检查文件污染 — DSH 本地构建 - Google Chrome')`，`FG 后` **完全相同**（同一个 hwnd/pid/标题）。
  - 窗口集合差 = `[] []`（前 7 个、后 7 个，逐字相同）；剪贴板 `逐字相同 = True`（前后长度都是 0，没被 `set_clipboard\` 清空动作碰过）。
- **结果**：**PASS**
- **缺口（不隐瞒）**：这一轮 `自起窗口候选数 = 0`（当时 jarvis 的窗口 pid 10988 不在 `_visible_windows()\` 的可见窗口里），所以**正面路径没走 `dispatch\`**，正面路径在第 3 轮补。教训：正面路径要在「窗口确定在」的状态下跑，不能靠上一轮的窗口。
