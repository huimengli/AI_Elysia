# 轮 2 · 2026-11-17-14-46

- **场景**：修好 `open_url` 复用判据后重跑 `play_music(first_bilibili_video('稻香'))`
- **期望**：导航到稻香 → 关弹幕 → 最低分辨率 640x360 → 时间前进 → 播完关窗
- **实际**（job pwsh-161 **exit code 1**）：
  - `open_url` 新建窗口（当时我起过的窗口全被轮 1 关掉），页面标题「【私藏馆】周杰伦《稻香》…_哔哩哔哩_bilibili」
  - 程序**崩溃**：`websockets.exceptions.ConnectionClosedError: no close frame received or sent`
    —— 在 `play_music` 的 `c.ev(STATE_JS)`（`browser_cdp.py` L90 `self.ws.send`）抛出
  - 崩溃后 14:48 复查（`.tmp/state_check.py`，同窗口 pid 19668）：
    `CDP 地址: https://www.bilibili.com/video/BV1Ki4y1y7HC/?vd_source=…`（**导航成功**，地址含 BV1Ki4y1y7HC）
    `分辨率 640x360`（**最低分辨率生效**）、`弹幕checked false`（**弹幕关闭**）、`ct=0 / du=223`
  - 进度前进与播完关窗**没有发生**（程序已崩，没跑到那两步）
- **结果**：**FAIL**（①导航 PASS、②关弹幕 PASS、③最低分辨率 PASS、④时间前进 未测、⑤播完关窗 未执行）
- **根因与修复（自曝）**：B 站页面加载时会重定向（`?vd_source=`），CDP target 的 session 被换掉，
  我复用的长连接随之断开。已改成**每次读数都新开一条连接**（`evaluate()` 一次性，不再保持长连接），
  读数解析失败/连接失败都如实写进日志并中断，不伪装成"播放了"
- **备注**：复查时 `ct=0`，即视频停在 0 秒 —— 轮 3 若时间不前进，如实报「未播放」
