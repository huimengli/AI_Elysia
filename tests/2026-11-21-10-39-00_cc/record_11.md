# 轮 11 · 搜索兜底（bing 兜底路径）

- 时间：2026-11-21 11:15:53
- 场景：收尾：关我自己起的浏览器窗口（轮 7-8 起过）
- 期望：关后我起的窗口数 = 0
- 实际：关前 0 → 关后 0 | 我起的浏览器窗口 0 个（上限 3，你的窗口不计）：。浏览器窗口共 1 个。没有我起的窗口（记录文件里没有可对应的 pid），没有可关的对象。
- 结果：**PASS**
- 备注：只关 jarvis 自起 pid（profile 认 pid），不碰你的窗口

**平凡通过照实写**：关前 0、关后 0，没有窗口可关。机制第一手：`_jarvis_profile_pids()` 在我沙箱里跑不了（它用 `powershell` + `capture_output`，即 piped stdio，被沙箱拒 → `except` 吞掉返回空集），`PID_FILE` 42 条历史 pid 随进程死亡；`_browser_windows()` 只看到 DSH 窗口 pid 5244（不计）。轮 7-8 起的 jarvis 窗口在我程序结束时一起被杀（11-18/11-20 已记过的已知环境事实）。

`pwsh` 独立复核（不经过 jarvis 代码）：`Get-CimInstance Win32_Process` 查 `chrome.exe` 带 `chrome_profile` 的进程 → **0 条**。

证据：`.tmp/logs/search_rounds.json`；驱动 `.tmp/search_test.py`（轮 7-8 真机部分）与 `.tmp/search_test2.py`（轮 9-11，stub 返回 (json, err) 二元组——第一版返回单串被 `s, e = evaluate(...)` 解包炸，第 61 处自曝）。
