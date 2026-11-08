# 轮 1：现场追踪真人语音（2026-11-08-19:58）

- 场景：job pwsh-44 加 `[ABORT] set by …` 与 `[Wake] barge-in score=… recording=…` 后，请用户说「爱莉希雅」→「现在几点了？」。
- 期望：判定是谁把录音打断（唤醒 barge-in / UI 中止 / WS interrupt / Esc）。
- 实际：`Wake word detected!` → `Recording...` → `Mic paused` → `[STT] Recording aborted.` → `Recorded 0.3s of audio` → `Transcription empty`；伴随 `[Wake] barge-in score=0.664 recording=False` + `[ABORT] set by listen_for_wake_word:132`（后一版行号 135）。转写只剩 `You`/`爱丽西亚`/`幾秒` 这类碎片；19:53 的 WS 也被回 `已停止。`。
- 结果：**PASS（根因确证）**
- 备注：`record_until_silence` 每 chunk 查 `_abort_event`；`_busy` 锁在整轮持有；IDLE 冷却只有 2 s，挡不住她的 ack『在。』+ 用户紧接着说话；`_stt_recording` 旧代码只在 `time.sleep(0.15)` 之后置 True，所以 busy 分支看到 `recording=False` 就 `abort_all()`。
