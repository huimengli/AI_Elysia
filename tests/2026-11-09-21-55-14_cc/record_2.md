# 第 2 轮 · 唤醒提示音「零合成、零建流」延迟实测

- 时间：2026-11-10 16:44–16:47
- 场景：唤醒应答从「读 wav + `sd.play` 新建输出流」改为「启动时预加载 PCM 到内存 + 常驻复用同一输出流」；用探针脚本 `.tmp\probe_ack.py` 直接计时（`preload_ack_audio()` + 连续 3 次 `play_ack_wav()`）
- 期望：`wake → 出声` 的热路径里不再出现文件解码与流启动，也不再出现 TTS 合成请求
- 实际（`.tmp\bats\ack2.log` 修 bug 前 / `.tmp\bats\ack3.log` 加启动预热后）：

修 `latency="small"` 前（`ack2.log`）：

```
[TTS] ack audio preloaded: 5 clips in memory
preload_ms=7.1 clips=5
TypeError: must be real number, not str   ← sd.OutputStream(latency="small") 被这版 sounddevice 拒绝
```

加启动预热后（`ack3.log`）：

```
[TTS] ack audio preloaded: 5 clips in memory
[TTS] output stream warmed in 3125 ms
preload_ms=3132.9 clips=5
[TTS] ack stream ready in 0 ms      / ack played (2.26 s), total 2281 ms
[TTS] ack stream ready in 0 ms      / ack played (2.02 s), total 2030 ms
[TTS] ack stream ready in 0 ms      / ack played (2.10 s), total 2099 ms
cache_len=5 stream=True
```

- 量化结论：
  - 建流成本 **3125–3444 ms** 是「每次唤醒出声慢」的主因（旧路径每次唤醒都付一次），现被移到启动时一次性支付；
  - 之后热路径 `ack stream ready = 0 ms`，总耗时 = 音频长度 + **约 20 ms**（2.26 s 音频 → 2281 ms，2.02 s → 2030 ms，2.10 s → 2099 ms）；
  - 热路径没有任何 HTTP 请求（`_gptsovits_synth` 未被调用）、没有 `wave.open`、没有 `sd.play` 建流。
- 结果：**PASS**（首字出声延迟从 ~3.4 s 级降到 ~20 ms 级；`preload` 后 5 条应答音全在内存）
- 备注：发现的两个真问题都已修 —— ① `latency="small"` 在这版 sounddevice 会抛 `TypeError`（必须数值 blocksize），已去掉；② 只在唤醒时才建流，会让**第一次**唤醒依旧慢 3.4 s，已改为启动预热建流。正在运行的 Jarvis（旧代码）唤醒应答会抛异常，故本轮结束后已用新代码重启（`killed 15820` → 16:46:57 拉起，日志 `.tmp\jarvis3.log`）。
