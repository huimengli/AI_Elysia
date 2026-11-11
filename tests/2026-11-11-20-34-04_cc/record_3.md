# 轮 3 — 中途打断（barge-in）时队列立即停止（2026-11-11 20:43）

- 时间：2026-11-11 20:43（`.tmp/probe_tts_queue.py` 轮 3：播放开始后 1.2 s 调 `stop_speaking()`，日志 `.tmp\bats\ttsqueue2.log`）
- 场景：队列播放长应答，1.2 s 后打断；`stop_speaking()` 现在会 `_interrupt.set()` + **flush 复用输出流**（只 `sd.stop()` 不够，队列里的缓冲会播完）
- 期望：播放立刻停止、producer 停止后续合成、`is_speaking()` 变 `False`、`speak_queued()` 及时返回
- 实际：`[TTS] queued: 6 segments, first sound n/a, played 0.00 s, total 2363 ms (interrupted)`；`speak_queued` 在打断后 2363 ms 返回，`is_speaking=False`；`played 0.00 s` = **没有播出任何音频**（首段 2.4 s 到队列时已检测到打断，直接丢弃）
- 结果：**PASS**
- 备注：`main.py` 的 barge-in 路径（唤醒时 `if is_speaking(): stop_speaking()`）未改，语义不变；返回耗时 ≈ 首段合成剩余时间，属 producer 线程的收尾，无残留播放
