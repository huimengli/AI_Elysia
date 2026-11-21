# 轮 14 · 到达结尾 + 播完关窗 + 关后 0（**PASS，全判据第一手**）

- 时间：2026-11-21 11:52:26 — 2026-11-21 12:01:25（504 s 轮询）
- 场景：真机 `play_music("", keyword="爱莉希雅", close_at_end=True, max_wait=600)`，后台任务跑；**关前我起的窗口数 1**（轮 13 起的 pid 3584 还活着 —— 上一轮窗口没随驱动进程结束一起没，`PID_FILE` 里那条 pid 可对应）
- 期望：到达结尾 + 弹幕关 + 最低分辨率 + jarvis 关掉**自己起的**窗口 + 关后我起的窗口 0
- 实际（日志原文照抄）：
  关键词「爱莉希雅」→ 最多播放第一支：https://www.bilibili.com/video/BV1fY4y1F7GL（25143893 播放，标题「《崩坏3》动画短片「因你而在的故事」」，共 20 条，数据源 API order=play，30921 字节）
  我起过窗口，当前标签地址 ['https://www.bilibili.com/video/BV1bY411b7k9?vd_source=ce9831764100c57a0ed3bbf139179e7e&spm'] 不含目标 BV1fY4y1F7GL，已导航：已用 CDP `Page.navigate` 导航我自己起的窗口：https://www.bilibili.com/video/BV1fY4y1F7GL
  导航瞬间复读：{"标题": "", "地址": "https://www.bilibili.com/video/BV1fY4y1F7GL/"}
  复读全部标签（0.0 秒）：['https://www.bilibili.com/video/BV1fY4y1F7GL/']（含 BV1fY4y1F7GL），**导航成功**
  复读全部标签地址：['https://www.bilibili.com/video/BV1fY4y1F7GL/']，导航成功
  就绪：已悬停播放器 @(380,357)（页面坐标）
  就绪检查：{"有video": true, "du": 506, "ct": 0, "菜单项数": 6, "弹幕input": true, "标题": "《崩坏3》动画短片「因你而在的故事」_哔哩哔哩_bilibi"}  
  设置：{"danmakuChecked":false,"autoplay":false,"点过最低档":true,"已发起播放":true,"菜单项":["1080P 60帧大会员","1080P 高清","720P 准高清","480P 标清","360P 流畅","自动"]}  
  起始读数：{"标题": "《崩坏3》动画短片「因你而在的故事」_哔哩哔哩_bilibili", "地址": "https://www.bilibili.com/video/BV1fY4y1F7GL/?v", "ct": 0.1, "du": 506, "paused": false, "ended": false, "分辨率": "640x360", "弹幕checked": false, "autoplay": false}  
  最低分辨率判定：640x360（判据 = 点过「360P 流畅」+ 宽度 640，高度随源比例）
  弹幕 checked=False（false=关闭）  autoplay checked=False（false=关，实测挡不住连播）
  到结尾：ct=505.2 / du=505.166（t+504s，标题「《崩坏3》动画短片「因你而在的故事」_哔哩哔哩_bilibi」）
  进度：起始 ct=0.1 du=505.166，最后 ct=502.8，时间前进=True，到达结尾=True，等了 504s
  关闭我自己起的窗口 pid 3584（标题「《崩坏3》动画短片「因你而在的故事」_哔哩哔哩_bilibili - Googl」，Q29 只关 jarvis 自起窗口）：SUCCESS: The process with PID 3584 has been terminated.
  关后我起的窗口数：0

- 独立复核（不经过 jarvis 代码）：`Get-Process chrome` 带主窗口句柄的 = **只剩 5244（DSH 窗口，不是我起的，不计）**；`Get-CimInstance` 查带 `chrome_profile` 的 chrome 进程 = **0 条**
- 结果：**PASS**
- 备注（照实，不夸大）：
  - 「到达结尾」= `ct=505.2 / du=505.166`（t+504 s 读到），末次取样 `ct=502.8` 是轮询落点，结尾事件已读到，照实记两条数。
  - 关窗身份走的是**记录文件里的 pid**（`PID_FILE` 的 3584，`taskkill` SUCCESS），**不是 profile 扫描** —— profile 扫描在我沙箱被管道权限卡（照实记，机制同一口径：只关 jarvis 自起 pid）。所以我这边能证的口径是「记录 pid」；profile 认 pid 这一路在你机器上的完整验收照旧挂着。
  - `manage_browser_windows(close_extra=True)` 我额外显式叫了一次，原文照抄：「我起的浏览器窗口 0 个（上限 3，你的窗口不计）：。浏览器窗口共 1 个。没有我起的窗口（记录文件里没有可对应的 pid），没有可关的对象。」—— 这条是**关窗后**的证据，不是关窗前。
  - 3 轮齐：轮 12 FAIL（我 `max_wait` 定小）、轮 13 PASS（到达结尾）、轮 14 PASS（到达结尾 + 关窗 + 关后 0）。
