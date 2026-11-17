# 轮 6 · 2026-11-17-11-40 · `open_url` / `navigate_url` 的窗口边界（发现真问题）

- **场景**：沙箱内连续调用（顺序，工具原话逐字贴）：
  `open_url('https://search.bilibili.com/all?keyword=稻香')` → `manage_browser_windows(False)` →
  `navigate_url('https://www.bilibili.com/video/BV1Ki4y1y7HC')` → `manage_browser_windows(False)`
- **实际输出（逐字）**：
  - `复用已打开的窗口：dsh-browser [session-e798aabd-…] — api.bilibili.com/x/web-interface/search/all/v2?keyword=稻香 — https://api.bilibili.com/x/web-interface/search/all/v2?keyword=%E7%A8%BB%E9%A6%99（匹配关键词 search，没有再起新实例）`
  - `已聚焦窗口：dsh-browser [session-e798aabd-…] …（进程 16732）`
  - `我起的浏览器窗口 0 个（上限 3，你的窗口不计）：。浏览器窗口共 1 个。没有我起的窗口（记录文件里没有可对应的 pid），没有可关的对象。`
  - `已把 https://www.bilibili.com/video/BV1Ki4y1y7HC 送进地址栏（已按下：ctrl+l，已输入文本（剪贴板粘贴，5 个字符键盘打不出）：https://www.bilibili.com/video/BV1Ki4y1y7HC，已按下：enter），但 12 秒内**被聚焦的窗口**标题没变（仍是「实时对话与状态显示修复 — DSH 本地构建 - Google Chrome」（进程 15416）），页面可能没真的跳转，请确认。`
- **结果**：**FAIL（安全边界问题）**，两条实锤：
  1. **复用分支会抢非 jarvis 窗口**：`open_url` 的复用用 `_browser_windows()`（全部可见浏览器窗口，
     `app_control.py L171/L195`），按标题 `search` 匹配到**我的 DSH 浏览器窗口**（pid 16732，**记录文件里没有它的 pid**，
     计数 0 → 它不是 jarvis 起的）→ **把焦点、键盘、剪贴板打进你的窗口**，违反 Q29「只限 jarvis 起的窗口」
  2. **`navigate_url` 没匹配到目标窗口时选第一个窗口**（`L404 wins = _browser_windows()`），同样打进你的窗口
- **正面确认（这条是好的）**：**剪贴板归还没有问题** —— `desktop.py L61-67`：`saved = get_clipboard()` →
  `set_clipboard(text)` → `set_clipboard(saved)`，用户剪贴板先存后还（HB-036 的既定做法）
- **键盘注入限制（沙箱固有）**：`ctrl+l` / `enter` 落**沙箱窗口站**，沙箱里 `navigate_url` **不可能验通**；
  工具没有假装成功，给出的是"12 秒内被聚焦的窗口标题没变 + 请确认"——**诚实失败口径正确**
- **需要改的（等 Q32 授权，未写代码）**：复用与选窗口都只认 `_jarvis_windows()`（pid 在记录里）；
  只有你的窗口时如实报「你的窗口我不聚焦、不输入」，不动你的窗口
