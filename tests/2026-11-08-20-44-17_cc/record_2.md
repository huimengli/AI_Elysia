# 轮 2 — 距离 1 米说「爱莉希雅」

- **时间**：2026-11-13 11:55:15
- **场景**：离麦克风约 1 米，正常音量，只说唤醒词
- **期望**：恰 1 次检出、应答「在。」出声、无连续触发
- **实际**：
  - 事件库：`11:55:15 wake Wake word triggered` → `11:55:20 system Wake: no voice recognized`
  - 日志（顺序对应）：`Wake word detected!` → `ack stream ready in 0 ms` → `ack played (2.10 s)` → `Transcription empty` → `ack[ack_no_heard] played (3.32 s)`
  - 与轮 1 间隔 11 s，与轮 3 间隔 15 s，均远大于 2.0 s 冷却
- **结果**：**PASS**。距离 1 米仍能检出 1 次，应答与空转录兜底都出声。
- **备注**：本轮起峰值仍无逐轮时间戳（采样器 12:02 才启动）。
