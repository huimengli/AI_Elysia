# 第 4 轮（补充）· 打断/中止在新播放路径上不回归

- 时间：2026-11-10 16:58
- 场景：常驻输出流 + 分块写流的播放路径，必须仍能响应 `stop_speaking()`（Esc、语音打断、barge-in、网页 `stop`/`interrupt` 全走这个函数）
- 期望：播放中途调用 `stop_speaking()` 立即出声停止、线程退出、`is_speaking()` 变 `false`，且流不被永久占死
- 实际（`.tmp\bats\stop1.log`，`.tmp\probe_interrupt.py`）：

```
[TTS] ack audio preloaded: 5 clips in memory
[TTS] output stream warmed in 990 ms
[TTS] ack stream ready in 0 ms
[TTS] ack played (2.26 s), total 537 ms      ← 2.26 s 音频在 0.5 s 处被打断
mid_is_speaking=True
stop_call_ms=0.0
thread_alive=False is_speaking_after=False
stream_active=False
```

- 结果：**PASS** — 打断调用 0 ms 返回，写流循环在 ≤100 ms（一个 0.1 s 块）内退出并 `stream.stop()` 清空队列；`_speaking` 与 `_interrupt` 在 `finally` 复位，`is_speaking()=false`，下次唤醒可立刻复用（`_output_stream()` 会在非 active 时重新 `start()`）
- 备注：`stream_active=False` 是打断后的预期状态（队列清空），下一次 `play_ack_wav()` 会重新 `start()`；`warmed in 990 ms` 说明建流成本随设备状态波动（前两次 3125/2868 ms），进一步印证「必须把建流挪到启动阶段」
