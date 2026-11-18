# 轮 3：打开github（2e）

- **时间**：2026-11-18 10:57（首测）/ 11:03（复测）
- **场景**：WS 文本 `打开github`，无语音、无视觉、无点击。
- **期望（口径 2e）**：浏览器打开 `github.com`（我自己起的窗口，地址复读为证）。
- **首测（10:57）实际**：**FAIL**
  - LLM 选 `open_app("github")` → 音近层回「没听准，最接近 Git GUI / Unity Hub / Git CMD（相似度 0.67）」；
    连试两次，又试 `open_app("git")` → 「4 个候选：Git Bash、Git CMD、Git GUI、Git Release Notes」；
    全程**没有调用 `open_site`**，github 一个字都没打开（我起的窗口 1，CDP 标签仍是百度）。
  - 根因：小模型在「打开 + 名词」上默认落到 `open_app`（应用表有 Git 系条目、音近层会主动给建议），
    `open_site` 的描述不足以压过它。这是**工具选择的引导缺失**，不是映射缺条目
    （映射里 github → https://github.com 本来就有，轮 4 证明映射没问题）。
- **修复（本轮内落地）**
  - `jarvis/main.py` 系统提示加路由规则：「打开 + 站点名（浏览器/github/b站/百度/自定义对象名）
    → **open_site**；绝不用 open_app 开网页（实测会命中 Sandboxie 存根）；桌面程序才用 open_app；
    拿到证据就停，不要补 get_open_windows / press_key / run_python」；
  - `jarvis/tools/browser_cdp.py` 新增 `navigate()`（CDP `Page.navigate`），
    `jarvis/tools/app_control.py` 的 `navigate_url` 主路径改 CDP（自曝两次编辑事故：
    `def evaluate` 被我吃掉、`play_music` 结尾两行被我删——都已补回并编译通过）。
- **复测（11:03）实际**：**PASS**
  - LLM 调 `open_site(site="github")` → 映射 `https://github.com`（来源 config.yaml sites，用户自定义优先）；
  - 证据：`已用 chrome.exe 带参数启动 https://github.com，并复读到**页面地址证据**：https://github.com/
    （含 github.com，标题「GitHub · Change is constant…」，扫全部标签，用了 1.0 秒，记录窗口 pid 10940 为我起的窗口）`；
  - snap：我起的窗口数 1（pid 10940），CDP 全部标签 1：`https://github.com/`；回复只一句「已成功打开 GitHub 页面。」
- **结果**：**PASS**（复测）。窗口计数 1 ≤ 3 ✓，地址证据 ✓，无视觉无点击 ✓，回复不铺空动作 ✓。
- **备注（自曝）**
  - 上一轮的百度窗口（pid 560）在这之间消失了：现场出现「无法更新 Chrome」「要恢复页面吗？」
    后该实例退出（chrome 自身更新/崩溃路径），计数从 1 变成 0，`open_site` 于是新起实例。
    我没有把这条算成「我关掉的」，日志里也没有关闭动作 —— 如实记为**不是我关的**。
  - github 在这台机器可直连（1 秒内标题落地），不需要兜底；若以后超时，`open_site` 会如实报
    「导航未证实」，不会谎称打开。
- **关联**：records/2026-11-18-10-17-23.md（2e）、record_1.md（同族假阴性）、tests/opinion.md。
