# 轮 2：录音 1.5s 宽限 + 5s 冷却 + 入口置 recording（2026-11-08-20:00）

- 场景：`stt.py` 的 abort 检查加 `time.time() - _start > 1.5` 宽限；`main.py` `handle_wake` 入口 `_stt_recording = True`（`finally` 清零）；`wake.py` IDLE 冷却 2 s → 5 s；`[ABORT]` 追踪加 thread 名。重启（job pwsh-48 → pwsh-50）。
- 期望：录音不再在第一 chunk 被砍；转写能拿到用户的句子。
- 实际：录音变长 —— `[STT] Speech detected (rms=0.0272)` → `Recorded 1.5s of audio`；事件库 217 行 user `现在几点了`（voice，非碎片）、220 行 `幾秒`；`Transcription empty — didn't catch anything` 在真人两轮后**不再出现**（209-221 行无 `Wake: no voice recognized`）。
- 结果：**PASS**
- 备注：1.5 s 之后仍可能被 barge-in 打断（用户说话时唤醒模型再次打分 → `barge-in score=0.657 recording=False` → abort），长句子会截断；已记遗留。
