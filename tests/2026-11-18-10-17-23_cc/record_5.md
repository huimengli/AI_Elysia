# 轮 5：搜索（2d，baidu 首选 / bing 兜底）

- **时间**：2026-11-18 11:06（轮 5）/ 11:11（5b）/ 11:14（5c）
- **场景**：WS 文本 `搜索 爱莉希雅 歌曲`，无语音、无视觉、无点击。
- **期望（口径 2d，records/2026-11-18-10-17-23.md）**：搜索 = **打开浏览器搜索页**，
  baidu 首选，baidu 被挡/落不到搜索页时 bing 兜底；判据是 CDP 复读的**地址+标题**；
  **只看搜索页**，不许顺手播歌。
- **轮 5（11:06）实际**：**核心 PASS + 越界 FAIL**
  - `web_search(query="爱莉希雅 歌曲")` → 复用我起的窗口，CDP `Page.navigate` 到
    `https://www.baidu.com/s?wd=...`，导航瞬间复读 `标题「爱莉希雅 歌曲_百度搜索」`、
    `复读全部标签（0.0 秒）：['https://www.baidu.com/s?wd=...']（含 www.baidu.com/s），**导航成功**` ✓；
  - **越界**：模型接着调 `play_music(keyword="爱莉希雅")`（用户只说搜索），把搜索页换成
    B 站视频 `BV1fY4y1F7GL`（《崩坏3》因你而在的故事）。play_music 阻塞 900 s，驱动 60 s 收完
    没有回复（`回复: []`）。
- **轮 5b（11:11，加了提示词路由规则后）实际**：**核心 PASS + 越界仍在**
  - baidu 搜索页证据同轮 5（新起窗口 pid 2556，标题「爱莉希雅 歌曲_百度搜索」）✓；
  - 模型又调 `media_control(pause)` + `play_music(keyword="爱莉希雅 歌曲")` → 播了
    `BV11a411R7AM`（『TruE』——致以无暇之人）。
  - **自曝**：小模型（Qwen3.5-2B）对「搜索时不要顺手播歌」这条提示词**不遵守**，两轮连犯。
- **修复（本轮内落地）**
  - `jarvis/main.py` 加**分发层硬闸门** `_exec_tool_with_retry`：`play_music` 调用前读
    `_last_user_text`（本轮用户原文），话里没有播放动词（播放/播/放歌/放一首/来一/听/唱）就
    **拒绝执行**并如实回「没有播歌：这句话里没有播放指令（原文…）」，不放歌、不谎称。
  - 提示词同时保留「搜索只调用 web_search，play_music 只在明确播放时调用」。
- **轮 5c（11:14，带闸门）实际**：**PASS**
  - `web_search` 同证据 ✓（窗口 pid 7924，标题+地址为证，我起窗口数 1 ≤ 3）；
  - **没有再调 `play_music`**（闸门 + 提示词生效，WS 里没出现 play_music 调用）；
  - 新的自曝：模型改用 `get_time`（没被问）和 `run_python` 抓 baidu HTML，
    `from bs4 import BeautifulSoup` → `ModuleNotFoundError`（如实报 traceback，没有谎称结果）。
    要看结果应走 `read_screen` / `find_on_screen`（我起的窗口可读），已补提示词规则。
- **结果**：**PASS**（2d 核心：baidu 打开 + 地址标题证据 + 不播歌）。bing 兜底这条**本轮未触发**
  （baidu 每次都落到搜索页）→ 兜底路径**未测**，留后续轮制造触发（如 baidu 被挡时）。
- **备注（自曝）**
  - 轮 5/5b 的播歌把搜索页覆盖了，等于**破坏了搜索结果的可见性**；那两轮搜索证据仍然成立，
    我按「核心 PASS + 越界 FAIL」记，没有把越界说成符合期望。
  - bs4 不在 `.venv` 里；我没有擅自装依赖（`requirements.txt` 变更需你同意）。
- **关联**：records/2026-11-18-10-17-23.md（2d）、record_3.md、record_4.md、tests/opinion.md。
