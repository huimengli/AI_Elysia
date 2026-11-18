# 轮 4：打开b站（2f）

- **时间**：2026-11-18 10:55（首测）/ 11:04（复测）
- **场景**：WS 文本 `打开b站`，无语音、无视觉、无点击。
- **期望（口径 2f）**：浏览器打开 `bilibili.com`（我自己起的窗口，地址复读为证，复用优先）。
- **首测（10:55）实际**：**部分（工具对、导航未证实）**
  - LLM 正确调 `open_site(site="b站")` → 映射 `https://www.bilibili.com`（config.yaml 用户自定义优先）✓；
  - 导航走**键盘路线**（`focus_window` + `ctrl+l` + `type_text` + `enter`），12 秒后被聚焦窗口标题没变，
    复读地址仍是 `https://www.baidu.com/` → 工具如实报「**导航未证实**」（没有谎称成功）；
  - LLM 之后补 `focus_window` + `press_key("ctrl+l")` 两步空动作，回复叙述按键。
  - 根因：同一 Chrome 实例带着 chrome 自己的「要恢复页面吗？」「无法更新 Chrome」弹窗抢焦点，
    键盘输入的地址栏操作落在弹窗上，主窗口地址栏没动。键盘路线在这种现场不可靠。
- **修复（本轮内落地）**：`browser_cdp.navigate()` 用 CDP `Page.navigate`，`navigate_url` 主路径改 CDP
  （丙方案口径：无焦点、无键盘、无视觉、无点击），验证改**扫全部标签的地址**（`pages()`，
  自曝 `open_cdp("")` 只取第一个 page target 的多标签假阴性）。
- **复测（11:04）实际**：**PASS**
  - `open_site(site="b 站")`（LLM 带空格，映射按 `strip().lower()` 归一后命中）→ `https://www.bilibili.com`；
  - 证据：`我起过窗口，当前标签地址 ['https://github.com/'] 不含目标 www.bilibili.com，已导航：
    已用 CDP Page.navigate 导航我自己起的窗口` + `导航瞬间复读 {"标题":"哔哩哔哩 (゜-゜)つロ 干杯~-bilibili",
    "地址":"https://www.bilibili.com/"}` + `复读全部标签（0.0 秒）：['https://www.bilibili.com/']（含 www.bilibili.com），**导航成功**`；
  - **复用同一个窗口**（pid 10940，没有新起实例）→ 我起的窗口数 1 ✓，播歌唯一性不破坏。
- **结果**：**PASS**（复测）。复用优先 ✓，地址证据 ✓，无视觉无点击 ✓，窗口计数 1 ≤ 3 ✓。
- **备注（自曝）**
  - 首测 LLM 补的两步空动作（focus_window / press_key）在复测消失（系统提示加「拿到证据就停」后
    两轮回复都只一句），说明引导有效；保留观察。
  - 键盘路线代码已不再是主路径；`desktop.press_key/type_text` 仍是通用工具，我没有削弱它们，
    只是导航不再依赖它们。
- **关联**：records/2026-11-18-10-17-23.md（2f）、record_3.md、tests/opinion.md。
