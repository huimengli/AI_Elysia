# 第 2 轮（真机 · 你 15:36:21 那一次）· 吃尾截录音

- **时间**：15:36:18–15:36:28。三服务全在。
- **期望**：同四条判据。
- **实际（逐字日志）**：
  - `15:36:18 [Wake] peak 0.765` → `15:36:21 [爱莉希雅] Wake word detected!` → `ack played (2.10 s), total 2118 ms` **触发 ✓**
  - `15:36:21 [Duck] 没有暂停任何播放（CDP 连不上：CDP 端口 9333 连不上（没有我起的窗口带 --remote-debugging-port））` **新根因证据：播歌窗口没有调试端口 → Duck 无法暂停 B 站的播放**
  - `15:36:23 [爱莉希雅] Recording...` → `15:36:25 [STT] Recording aborted.` → `capture saved (1 s)` → `Recorded 1.5s` → `15:36:25 [爱莉希雅] Transcription empty — didn't catch anything` **判据② FAIL：录音被截到 1.5 s，转录空**
  - `15:36:28 [TTS] ack[ack_no_heard] played (3.32 s), total 3158 ms`
- **结果**：**FAIL**（判据②①不中）。
- **备注**：与 HB-048 第 1 项同现场（`ack → Recording aborted → capture 1 s`）。`stt.py:286-294` 的 1.5 s 保护在，1.5 s 之后中止标志一置位就 `break`。这一轮中止的来源是播歌期间她自己的声音/背景播放声 —— 结合上一行的 CDP 连不上，**播歌窗口不可暂停 = 播歌时的录音必被截**。
