# 第 4 轮（真机 · 15:52:22）· 你关窗后的第一环
- **时间**：15:52:22–15:52:29。三服务全在；`jarvis_windows=0`（你手动关掉她起的窗口后，计数为 0）。
- **期望**：四条判据（①转录含当轮歌名 ②无 `Recording aborted.` ③关键词逐字一致 ④播不播由你耳确认）。
- **实际（逐字）**：`15:52:22 [Duck] 没有暂停任何播放（CDP 连不上：CDP 端口 9333 连不上（没有我起的窗口带 --remote-debugging-port））` → `Wake word detected!` → `ack played (2.26 s)` → `Recording...` → **`15:52:25 [STT] Recording aborted. → capture saved (1 s) → Recorded 1.5s → Transcription empty`** → `ack[ack_no_heard] played (3.32 s)`。
- **结果**：**FAIL**（判据②①不中）。
- **备注**：关窗后 CDP 端口随窗口消失，Duck 每次唤醒前都报连不上（15:52:22、15:52:44、15:54:46、15:56:57 四份逐字）。同链的还有 15:37:02 `[Tool: music_control] 恢复失败（CDP 连不上…）`、15:37:11 `[Tool: read_page] 读不到页面文本（CDP 连不上…）`。
