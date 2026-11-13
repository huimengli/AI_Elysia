# 轮 3 — 侧向 45°（头转开）说「爱莉希雅」

- **时间**：2026-11-13 11:55:30
- **场景**：头转开约 45°、不正对麦克风，说唤醒词
- **期望**：恰 1 次检出、应答「在。」、无连续触发
- **实际**：
  - 事件库：`11:55:30 wake Wake word triggered` → `11:55:35 system Wake: no voice recognized`
  - 日志（顺序对应）：`Wake word detected!` → `ack stream ready in 0 ms` → `ack played (2.58 s)` → `Transcription empty` → `ack[ack_no_heard] played (3.32 s)`
  - 与轮 2 间隔 15 s、与轮 4 间隔 13 s
- **结果**：**PASS**。侧向 45° 仍检出 1 次。
- **备注**：同前，峰值无逐轮时间戳。侧向是 v0.9 的已知强项（正样本以麦克风前真人录音为主），本轮没有反例。
