# 验证轮 2 — WS 监控协议与推送节拍

时间：2026-11-21 16:15（首跑）→ 16:26（global 修复后复跑），沙箱内 TestClient websocket_connect("/ws")
场景：WS 收 `monitor_config`（间隔 1-30 s，Q30-3），服务端按节拍推 `monitor`（快照 + 四灯 + 日志批次）。驱动用带超时的 recv 防卡死（第 102 处自曝：首版驱动 120 s 撞死，16 分钟没出结果）。
期望（design v3.1 §3 Q30-3）：
1. `connected` 后发 `monitor_config{interval:1}`，服务端节拍变为 1 s。
2. 之后每拍约 1 s，类型 `monitor`。
3. 间隔夹取：100 → 30，0 → 1。
4. 无监控客户端时不空转（要 sleep）。

实际（复跑 16:26，逐字）：
```
[Web] Event loop captured — WebSocket broadcast ready.
[Apps] {'added': 0, 'skipped_existing': 243, 'no_target_skipped': 5, 'pinyin_filled': 227, 'total': 227}
轮2 首条 connected
轮2 首拍 monitor 用时 14.87 节拍 1
轮2 第2拍 monitor 间隔 4.66
轮2 第3拍 monitor 间隔 4.26
轮2 夹后节拍（100→30, 0→1） 1
轮2 收工
```
首跑（16:15，global 未修）是 `节拍 5 / 第2拍 5.22 / 第3拍 4.93`——第 105 处自曝：`monitor_config` 分支给 `_mon_interval` 赋值少了 `global`，赋值变局部变量，全局节拍永远停在 5。

结果：**部分 PASS**。协议面 PASS（首条 connected、类型 monitor、100→30 与 0→1 夹取后节拍 = 1、无客户端 sleep 已加）；**节拍 1 s 未达**：实测 4.26-4.66 s/拍，第 1 拍 14.87 s。
备注：
- 节拍被**单拍采样耗时**压住：沙箱内 8080/9880 未监听，四灯探针要等 TCP 超时；`svc.snapshot()` 首次调用要付 `app_control` 建 243 项应用索引的成本（日志里 `[Apps] pinyin_filled 227` 就是它）；`listen_pids` 走 `netstat -ano` 单拍再花 0.2-0.4 s（第 111 处自曝后改用 netstat，见 record_3 追加段）。节拍补偿已加（`sleep(max(0, interval - 耗时))`），所以拍间隔 = 采样耗时，不是 sleep。
- 真机（服务在跑、探针秒回）能不能真到 1 s，沙箱内**不可测，记未测**。
- 前端页面（间隔下拉、隐藏页降 30、日志区折叠、关闭按钮 confirm）在沙箱里没打开过：**未测**，要你在真会话里看。
