# 轮 8 · 2026-11-17-12-16 · **第一次真跑通 Route A**（沙箱内，`navigate_url` 验通）

- **场景**：改完三处（`open_url` 复用只认 jarvis 自起窗口、`navigate_url` 只在我起窗口导航、`first_bilibili_video` 改 API `order=play`）后，
  沙箱内顺序跑 `open_url` → `navigate_url` → `manage_browser_windows`（工具原话逐字）：
  - `[1 open_url]` `复用我自己起的窗口：稻香-哔哩哔哩_bilibili - Google Chrome（匹配关键词 稻香，没有再起新实例）`
    `已聚焦窗口：稻香-哔哩哔哩_bilibili - Google Chrome（进程 9952）`
  - `[2 navigate_url]` `已在被聚焦的窗口导航：基准「稻香-哔哩哔哩_bilibili - Google Chrome」（进程 9952）->
    现在「【私藏馆】周杰伦《稻香》超治愈神作！希望疫情早点过去_哔哩哔哩_bilibili - Google Chrome」（已按下：ctrl+l，
    已输入文本（剪贴板粘贴，5 个字符键盘打不出）：https://www.bilibili.com/video/BV1Ki4y1y7HC，已按下：enter，用了 **1.0 秒**）`
  - `[3 manage]` `我起的浏览器窗口 **1** 个（上限 3，你的窗口不计）：【私藏馆】周杰伦《稻香》…_哔哩哔哩_bilibili - Google Chrome。
    浏览器窗口共 **2** 个。未关闭任何窗口。`
- **期望（判据，19:18 你定的口径）**：不最大化窗口、标题变视频页、`<video>` 在播
- **实际**：**标题判据 PASS**（1.0 秒内变视频页标题，pid 9952 是 jarvis 记录窗口，`manage` 计数 1）
  **播放判据 未取证**：截图里播放器可见、弹幕已渲染（「java前端学员现状」「你在加速」）、「12人正在看」、播放数 **948.6 万**
  （与 API `play 9,488,894` 对得上）、中间有 play 三角（悬停态）；**时间进度条没截到**（裁底部 `y 495-550` 是全黑），
  **OCR 与视觉服务都不可达**（`http://127.0.0.1:50015` 未开，WinRT 这台机不可用，llama `:8080` 被我杀）→ 无法读时间数字
- **结果**：**PASS（Route A 端到端在沙箱跑通）**，并**作废我自己两条判断**：
  1. **`navigate_url` 在沙箱可以验通** —— 我此前说"键盘注入落沙箱窗口站，不可能验通"是**错的**：真原因是之前敲进的是
     DSH 的 Electron 窗口（它的地址栏不是标准 Chrome 的，`ctrl+l` 无效果），**不是注入进不去**。
     在 jarvis 自起的 Chrome 窗口里，`ctrl+l` + 粘贴 + Enter **1 秒内改标题**
  2. **复用分支改对之后不再打进你的窗口**：`open_url` 文本变成「复用**我自己起的**窗口」，`navigate_url` 在你只有窗口时
     如实停手（上一轮实测文本：「我自己起的浏览器窗口 0 个（浏览器窗口共 1 个）。**你的窗口我不聚焦、不输入**，…未打开」）
- **备注**：**我自己引入的回归已在本次修掉**（把 `_visible_windows` 的导入删了，`L250` 记录 pid 时 `NameError`，
  第一次测试当场暴露 → 补导入后通过）；jarvis 起的窗口 pid 9952 仍在桌面（`manage_browser_windows` 未关，上限 3 未满，Q24 你手动关）
