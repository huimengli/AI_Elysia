# 轮 1 · 2026-11-17-14-36

- **场景**：`play_music(first_bilibili_video('稻香'))` —— 把**带解说的整句**喂进去，只听歌模式（关弹幕 + 最低分辨率 + 播完关窗）
- **期望**：① 导航到稻香 BV1Ki4y1y7HC ② 弹幕关闭 ③ 最低分辨率 640x360 ④ 时间前进 ⑤ 播完关掉我自己起的窗口
- **实际**（job pwsh-158 exit 0，逐条证据）：
  - `open_url` 走**复用分支**：「复用我自己起的窗口：【4K60FPS】周杰伦《夜曲》…（匹配关键词 bilibili，没有再起新实例）」—— 当时页面是**《夜曲》BV1Lh411t7jQ**，**没有导航到稻香**
  - 设置：`danmakuChecked=false`（关）、`autoplay=false`（关）、点过最低档、菜单项含「360P 流畅」
  - 最低分辨率判定：**640x360** ✓
  - 起始读数 ct=40.7 / du=230.233；到结尾 ct=229.8/du=230.233（t+189s）；时间前进=True ✓
  - 关窗：`taskkill /PID 19048 /T /F` SUCCESS（8 个子进程 + 19048 本体），关后我起的窗口数 **0** ✓（Q29 只关 jarvis 自起 pid）
- **结果**：**部分 FAIL** —— ②③④⑤ PASS，**① 导航 FAIL**：播的是《夜曲》，不是稻香
- **备注（自曝）**：`open_url` 的复用判据是**注册域名关键词 `bilibili`**，任何 B 站窗口都算命中；窗口标题**不含 BV 号**，所以标题证据天生无法判页面身份。已改：页面身份用 CDP 的 `location.href` 对 BV 号（`_url_identity`），地址不含目标就导航并复读地址、导航未证实就不算成功。
- 新增能力：`jarvis/tools/browser_cdp.py`（CDP 客户端：`targets`/`open_cdp`/`evaluate`/`real_click`/`kill_recorded_pid`）、`app_control.play_music`、`jarvis_pids()`（公开，只用于校验可关 pid）
- Chrome 启动参数加 `--remote-debugging-port=9333`（jarvis 自己的窗口与 `.tmp/chrome_profile`，127.0.0.1）
