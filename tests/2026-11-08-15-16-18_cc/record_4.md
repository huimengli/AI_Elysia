# 轮 4：C: 清理后重装（2026-11-08-16:58）

- 场景：用户清理 C: 空间（`wmic` 实测 C: 剩 6 GB），重跑 `npx playwright install chromium-headless-shell`；先前在 30% 报 `ENOSPC`，清理后不再报。
- 期望：无 ENOSPC；下载完成并安装到 `ms-playwright`。
- 实际：前台 540 s 与后台 job pwsh-3 均到 **40%** 后被 `ECONNRESET`（`cdn.playwright.dev:443`）打断，job 退出码 1；`C:\Users\楼听\AppData\Local\ms-playwright` 只剩 `.links`。→ **磁盘问题已消除，但官方安装器无法在慢速/易断连的网络上跑完 114.6 MiB。**
- 结果：**部分 PASS（ENOSPC 消失）/ 安装未完成**
- 备注：改走自管下载 + 手工布局（见轮 5）。
