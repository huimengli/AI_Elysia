# 轮 6 · 2026-11-16-15:20-02

- **时间**：15:30 重启 7860（`start7860_1530.log`），15:20:02 点击，15:20:18 读数
- **场景**：`desktop.py` 的 `get_open_windows`/`focus_window` 改为**进程内 ctypes**（`_visible_windows()`，user32 函数带 argtypes/restypes）；`open_url` 给 Chromium 加 `--new-window`
- **期望**：`open_url` 复读到含「稻香」的窗口标题，然后点第一支视频播放
- **实际**（日志 L37-47 + 事件 + 窗口列表）：
  - `[Tool: open_url] 已用 chrome.exe 带参数启动 https://search.bilibili.com/all?keyword=稻香，并复读到窗口证据：稻香-哔哩哔哩_bilibili - Google Chrome（进程 8228）（匹配关键词 稻香）` ✓ —— 证据分支真读到窗口标题
  - `[Tool: read_screen] 稻 杳 一 哔 哩 哔 哩 bilibili | 162,26` —— jarvis 读屏 + WinRT OCR 在服务里可用 ✓（**错字 稻→杳、字间插空格**，已知缺陷）
  - `[Tool: find_on_screen] 最接近的匹配：「Hi•Res」位于 (574, 576)` —— 中文分词 overlap 不可靠（已知待修），**没点到第一支视频**
  - 15:20:18 事件 `我执行了 打开网址、读取屏幕、屏幕查找：最接近的匹配：「Hi•Res」位于 (574, 576)，用 click_at 可点击。`
  - 4 灯 `wake=True asr=True llm=True tts=True`，`model=aili_xiya_v0.9.onnx thr=0.75`；提交 上限 29,812 / 已用 26,883 / **可用 2,929 MB**
- **结果**：**部分达标，且有一处必须披露的借用证据**：那个「稻香-哔哩哔哩_bilibili」标题是我**先前用 pwsh 工具 `Start-Process` 启动**留下的窗口；沙箱里 jarvis 自己 Popen 的 chrome **只出进程、不出可见窗口**（窗口站隔离）。所以「复读到窗口证据」这一轮**部分来自我造的窗口**，不是 jarvis 在沙箱里自己打开的。播放仍未达成。
- **备注**：副作用 —— pwsh 启动的 B 站窗口**未关**（进程 8228 仍在）。零截图。沙箱定论：**沙箱内 python 起的进程不能产生可见窗口** → 第 2 条的真端到端必须由你在沙箱外跑 jarvis 来验（`need_user.md` Q25）。
