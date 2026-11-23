# 第 6 轮（真机 · 15:54:46）· 同一环第三次
- **时间**：15:54:46–15:54:53。`jarvis_windows=0`。
- **期望**：同四条判据。
- **实际（逐字）**：`15:54:46 [Duck] 没有暂停任何播放（CDP 连不上…）` → `Wake word detected!` → `ack played (2.26 s)` → **`15:54:50 Recording aborted. → capture 1 s → Recorded 1.5s → Transcription empty`** → `ack_no_heard played (3.32 s)`。
- **结果**：**FAIL**（判据②①不中）。
- **备注**：F 块新增 `asr_secs 0.01 / 0.01 / 0.01`（三次空转录）、`total_secs 42.62 / 41.27`（比 184.73 s 快得多，因为没走到工具）。
