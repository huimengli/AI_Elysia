# 轮 3 — ASR 引擎 A/B（whisper 现役 vs sherpa-onnx Paraformer-zh small）

- 时间：2026-11-12 11:16-11:20（`.tmp\bats\asr_ab_r3.log`；前两轮 11:14-11:16 为 API 修正前的失败诊断，见下）
- 场景：同一批真实音频喂给两个引擎，逐条对比文本 / 耗时 / 与真值的字符相似度（`difflib` ratio）
  - 已知文本 6 件（文件名即真值，`C:\Users\楼听\Documents\录音`）
  - 12 条真实麦克风抓取（`.tmp\capture_*.wav`，`jarvis/stt.py` 每次录音落盘的原始 16 k PCM，records/2026-11-10-17-43-08.md 的「A/B 唯一依据」）
- 期望（records/2026-11-11-20-34-04.md 第 4 项）：两引擎都可用、可切换；若 sherpa 明显更好则设为默认
- 前置修复（本轮才跑通，前两轮记录为失败诊断）：
  - `asr_ab_r1.log`：probe 未带 HF 变量 → `LocalEntryNotFoundError`（whisper 去联网下载）。加 `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET` 后解决
  - `asr_ab_r2.log`：`OfflineRecognizer.from_paraformer() got an unexpected keyword argument 'paraformer_model'` —— sherpa-onnx 2.0.1 的签名是 `from_paraformer(paraformer, tokens, num_threads, ...)`，无 `paraformer_model` / `language_hints`
  - 再修正：`OfflineStream` 只有 `accept_waveform(sample_rate, samples)`（无 `accept_audio`）。`jarvis/stt.py` 已改并接上 `transcribe_audio` 的引擎分发（sherpa 空结果/异常回退 whisper）

- 实际（已知文本集，真值 = 文件名）：

| 真值 | whisper | sim | sherpa | sim | 耗时 whisper / sherpa |
| --- | --- | --- | --- | --- | --- |
| 爱莉希雅，帮我打开电视机 | 爱莉希雅帮我打开电视机。 | **0.92** | 爱丽丝雅帮我打开电视机 | 0.78 | 3702 / 2567 ms |
| 爱莉希雅，帮我打开浏览器 | 爱莉希雅帮我打开浏览器。 | **0.92** | 爱丽西雅帮我打开浏览器 | 0.78 | 4121 / **218 ms** |
| 你好啊爱莉希雅，你在干什么呢 | 你好啊,爱莉希,你在干什么呢? | **0.83** | 你好啊爱依希啊你在干什么呢 | 0.81 | 3745 / **228 ms** |
| 爱丽安娜 | 爱莉安娜 | 0.75 | 艾丽安娜 | 0.75 | 3278 / **142 ms** |
| 爱丽丝 | 爱莉斯 | 0.33 | **爱丽丝** | **1.00** | 3117 / **143 ms** |
| 米希雅 | 米西雅 | 0.67 | 米西雅 | 0.67 | 3167 / **150 ms** |

- sim ≥ 0.8 计数：**whisper 3/6，sherpa 2/6**。长句（18.30 s 真实抓取）：whisper 8218 ms vs **sherpa 418 ms**，文本质量相当（sherpa「你觉得我不敢吗」/ whisper「你觉得我不烦吗」）。
- **sherpa 的致命弱点**：12 条抓取里有 7 条几乎无人声，whisper（`vad_filter=True`）返回空串（正确，走「没听清」路径），**sherpa 没有 VAD，返回幻觉**：`嗯` / `嗯` / `有有逼` / `北京` / `你就我特我` / `小一瓶` / `啊`。在本项目里这些会被当作用户指令送进 LLM → 触发错误动作。
- 唤醒词书写：`capture_1794310430` whisper `爱莉希雅` / sherpa `爱丽希亚`；`capture_1794315282` whisper `爱莉希雅` / sherpa `泰利西亚泰利西亚`（重复幻觉）。sherpa 写不出正确的「爱莉希雅」。
- 结果：**PASS（引擎可选，达标）/ 不切换默认引擎**。whisper 在已知文本上 sim 更高（3/6 vs 2/6）、无人声时正确返回空、唤醒词书写正确；sherpa 快 10-20 倍（长句 418 ms vs 8218 ms，已知短句 143-228 ms vs 3117-4121 ms）但无 VAD → 静默幻觉，且写不出唤醒词正字。**`stt.engine` 保持 `whisper`**，sherpa 作为网页可选项保留（长句/低延迟场景可手动切换）。
- 下一批待办（写入 `todo.md`）：给 sherpa 路径加能量门（VAD/静音跳过），避免 `嗯` 类幻觉；在门生效后重跑 A/B 3 轮再决定是否设默认。
