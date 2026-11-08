# 轮 3：修「上一轮残留 abort 把录音砍成 0.3s」（2026-11-08-19:41）

- 场景：`record_until_silence` 每个 chunk 都查 `_abort_event`（`stt.py` 94-96 行），而 `_abort.clear()` 只在 `_process_request`（`main.py` 500 行）里做，**在录音之后**；`wake.py` 121-122 行在 busy 时喊醒词会 `abort_all()`，UI「中止」/Esc 同理 → 残留 flag 让下一轮录音第一 chunk 就 break（0.3 s）。修法：`_on_wake` 在 `pause_wake_mic()` 前显式 `_abort.clear()`（带注释）。重启（**job pwsh-38**）后真人语音走完整链路。
- 期望：wake → 录音 → 转写 → 回复不再被残留 abort 截断；UI/WS 正常。
- 实际：19:39:57 wake（173 行）→ `[STT] Speech detected (rms=0.0432)` → `Mic paused for STT recording.` → `Tool: type_text Typed: 我是爱莉希雅` → 回复链路完整，无 `Recording aborted.`；WS 复测 `好的，我是爱莉希雅。有什么我可以帮你的吗？`；`GET /` 200 / 42,420 B。
- 结果：**PASS**
- 真人测试提示：2B 把「说一句话/记一下」理解成 `type_text` 往桌面打字（本轮真机打了 `我是爱莉希雅`），先按「中止」（UI 中止 / WS `{"type":"interrupt"}` / Esc）；「爱莉希雅」仍常听成「爱利西亚」。阈值要更灵敏可设 0.60（设置页保存），0.75 是明确不可用的。
