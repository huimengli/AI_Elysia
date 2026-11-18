# 轮 1：打开浏览器（2a）

- **时间**：2026-11-18 10:41（首测）/ 10:52（复测）
- **场景**：用户不在电脑前，全程 WS 文本 + CDP 证据（无语音、无视觉、无坐标点击）。
  驱动 `.tmp/e2e_text_round.py`，WS `{"type":"chat","text":"打开浏览器"}`。
- **期望（口径 2a，records/2026-11-18-10-17-23.md）**：用**我自己起的**浏览器窗口打开，
  profile 认 pid（第 2 项口径），窗口计数 ≤3，判据是**页面地址复读**，不看页面外观。
- **首测（10:41）实际**：**FAIL**
  - LLM 选 `open_app("浏览器")` → 应用表子串匹配到「在沙盒中运行网页浏览器」
    （`C:\Program Files\Sandboxie\Start.exe default_browser`）；
  - 回读进程名 `Start` 被当成功 → 「已打开：在沙盒中运行网页浏览器（复读确认进程 Start）」
    = **启动器存根当应用进程，假成功**；
  - 之后 `get_open_windows` + `type_text`（把 `https://www.bilibili.com` 打进当时聚焦的窗口），
    我起的窗口数 0、CDP 标签 0；回复只叙述窗口列表。
  - 根因：① 应用表「浏览器」子串命中 Sandboxie 存根；② `apps.launch()` 回读只要求
    进程名 = exe stem，存根 `Start.exe` 天然满足；③ `open_app` 工具描述没有把
    「浏览器/网页」引到 `open_site`；④ 窗口标题判据用 `_url_keys` 英文关键词，
    中文标题「百度一下，你就知道」永远不含 `baidu`（`open_site` 首测也吃这条假阴性）。
- **修复（本轮内落地，已编译通过）**
  - `jarvis/apps.py`：`launch()` 加启动器存根黑名单（`start`/`launcher`/`runcommand`/`rundll32`），
    存根回读**如实不算成功**；
  - `jarvis/tools/app_control.py`：`open_app` 里浏览器词（浏览器/browser/网页浏览器/上网）
    **先走 `open_site`**；新增 `open_site()`（内置表 + `config.yaml` 的 `sites:` 用户自定义，
    优先级用户在前）、`music_control()`（第 3 项）；`open_url` 的启动轮询主判据改为
    **扫全部标签的页面地址含目标**（标题降为参考）；
  - `jarvis/tools/browser_cdp.py`：新增 `pages()` 扫全部标签（自曝：`open_cdp("")` 只取第一个
    page target，多标签时读到的不是活动标签）、`PAUSE_JS`/`RESUME_JS`/`PAGE_JS`、`duck()`；
  - `jarvis/tools/router.py`：`open_app` 描述明确「桌面程序专用，网页走 open_site，禁止用
    type_text 凑页面」；新增 `open_site` / `music_control` schema + TOOL_MAP + 中文 label。
- **复测（10:52）实际**：**PASS**
  - `open_app("浏览器")` → 「按浏览器口径走 open_site」→ `https://www.baidu.com`，
    `chrome.exe --no-sandbox --new-window --user-data-dir=.tmp\chrome_profile --remote-debugging-port=9333`；
  - 复读证据：`页面地址证据：https://www.baidu.com/（含 www.baidu.com，标题「百度一下，你就知道」，
    扫全部标签，用了 0.0 秒，记录窗口 pid 560 为我起的窗口）`；
  - snap：我起的窗口数 1（pid 560）；CDP 全部标签 1：`https://www.baidu.com/`。
- **结果**：**PASS**（复测）。窗口计数 1 ≤ 3 ✓，地址证据 ✓，无视觉无点击 ✓。
- **备注（自曝）**
  - LLM 复测后仍多跑两步无意义动作（`run_python` sleep 1、`get_open_windows`），回复叙述窗口列表；
    功能判据已满足，这条留给后续轮观察，需要时加提示词约束。
  - 同一 Chrome 实例（pid 560）出现「无法更新 Chrome」「要恢复页面吗？」窗口：
    chrome 自身崩溃恢复提示，属用户关注的内存/更新问题（HB-047 家族），我起的窗口计数只认
    标题匹配的可见窗口，这条不计入播歌窗口。
  - 现场残留：Sandboxie Control（pid 15076）、weixin update（pid 3352）——**不是我起的窗口**，
    是首测假启动的后续 UI，未计入我的窗口数。
- **关联**：records/2026-11-18-10-17-23.md（第 2a 项）、todo.md 同块、tests/opinion.md。
