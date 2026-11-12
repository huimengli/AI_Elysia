# 第 1 轮：预合成 + RAM 具名应答池（2026-11-12 23:08-23:10）

- 时间：2026-11-12 23:09（用户 23:06 选未完项 1「应答语预合成进 RAM 池」后开工）
- 场景：用现役 GPT-SoVITS `:9880/tts` 把「我没听清，请再说一遍。」预合成成 `jarvis/data/ack/ack_no_heard.wav`；`jarvis/tts.py` 的 `preload_ack_audio()` 加**统一采样率 + 具名缓存**，新增 `play_ack_phrase(name)`；`play_ack_wav()` 的轮播行为不变。探针 `training/_t2_ack_play_probe.py`，`NINST=3`
- 期望：6 条 clip 全部载入、统一采样率（避免第一次播具名句时重开输出流 ~3.4 s）；具名句可播且耗时 = 句长；打断后 `is_speaking=False`
- 实际：
  - `ack audio preloaded: 6 clips in memory（统一 32000 Hz，具名 ['ack_01'..'ack_05','ack_no_heard']）`，`ack_no_heard` = 3.32 s @ 32000 Hz、峰值 0.632，输出流预热 1012 ms；
  - 3 轮：`play_ack_wav` 2278/2030/2100 ms，`play_ack_phrase(ack_no_heard)` **3330/3300/3330 ms**（= 句长，流就绪 0 ms，无 TTS 往返）；
  - **打断**：播 0.35 s 后 `stop_speaking()` → 清队列 1219 ms、线程结束、`is_speaking=False`（barge-in 语义不变）；打断后那次播放总耗时 419 ms（提前终止）。
- 结果：**通过**。具名池可用，采样率统一后没有重开流代价；打断语义不变。
- 备注：零截图、无子智能体；`ack_no_heard.wav` 是音频产物，不入 Git（`.gitignore` 已排除 wav）。
