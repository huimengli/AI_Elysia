# 轮 3 · 2026-11-17-15-16

- **场景**：长连接修复后重跑 `play_music(first_bilibili_video('稻香'))`（复用已有窗口）
- **期望**：复用/导航到稻香 → 关弹幕 → 最低分辨率 → **时间前进** → 播完关窗
- **实际**（job pwsh-165 exit 0，无异常，全程如实）：
  - 复用判据用**地址证据**：`页面地址证据：https://www.bilibili.com/video/BV1Ki4y1y7HC/?vd_source=…（含 BV1Ki4y1y7HC），没有导航` ✓
  - `focus_window` **如实报前台锁**：「已找到窗口…（进程 19668），但系统拒绝把前台交给它（前台锁），请手动点击」
  - 设置：`danmakuChecked=false`、`autoplay=false`、点过最低档、菜单项含「360P 流畅」
  - 最低分辨率判定：**640x360** ✓
  - 起始读数：`ct=0`、`du=223`、**`paused=true`**
  - 进度：`起始 ct=0 du=223，最后 ct=0，时间前进=False，到达结尾=False，等了 900s`
  - 关窗：`taskkill /PID 19668 /T /F` SUCCESS（8 子进程 + 本体），关后窗口数 **0** ✓
- **结果**：**部分 FAIL** —— ①地址复用 PASS ②关弹幕 PASS ③最低分辨率 PASS ④**时间前进 FAIL（视频从未播放）** ⑤关窗 PASS（**是超时后关的，不是播完关的**）
- **根因（自曝）**：关掉「自动开播」后，B 站页面停在 `ct=0` **不会自己开始播**；`play_music` 里**没有播放动作**。轮 1 的时间能前进是因为那支《夜曲》是**已经在播**的页面。修法：设置后若 `paused=true`，用 CDP 派发**播放按钮的受信点击**（或 `video.play()`），再复读 `ct` 才判定播放
- 顺带确认：`--remote-debugging-port` + `Input.dispatchMouseEvent` 路线稳定，无长连接崩溃；`kill_recorded_pid` 只杀 jarvis 自起 pid（Q29）
