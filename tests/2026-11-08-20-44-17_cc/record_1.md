# 轮 1 — 正常音量、正对麦克风说「爱莉希雅」

- **时间**：2026-11-13 11:55:04
- **场景**：正对麦克风、正常音量，只说唤醒词「爱莉希雅」，说完自然停
- **期望**：恰 1 次检出（`last_detect` 更新）；应答「在。」出声；2.0 s 冷却内不重复触发
- **实际**：
  - 事件库：`11:55:04 wake Wake word triggered` → `11:55:10 system Wake: no voice recognized`
  - 服务日志（无时间戳，按顺序对应）：`[爱莉希雅] Wake word detected!` → `[TTS] ack stream ready in 0 ms` → `[TTS] ack played (2.02 s), total 1858 ms` → `Transcription empty — didn't catch anything.` → `[TTS] ack[ack_no_heard] played (3.32 s), total 3158 ms`
  - 下一轮触发在 `11:55:15`（间隔 11 s，远大于 2.0 s 冷却）
- **结果**：**PASS**。检出 1 次、应答「在。」2.02 s 出声、无连续触发。
- **备注**：本轮只说唤醒词没有后续语音，所以走的是「空转录 → `ack_no_heard`「我没听清，请再说一遍」（RAM 具名池，3.32 s）」路径，这正是第 19 轮的判据行为，此处顺带成立。**峰值未逐轮时间戳**（第 1-5 轮时没有采样器，`[Wake] peak` 行不带时间）；从第 6 轮起用 1.5 s 采样器 `.tmp/sampler_health.log` 补上。
