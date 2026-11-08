# 批次结论（tests/2026-11-08-19-25-48_cc，验证 3 轮）

- 「语音无法触发」的直接原因是 **阈值**：设置页保存的 `wake_word.threshold: 0.75` 高于真实环境峰值（真人 1.5 分钟 peak 最高 0.570），而干净合成音频 PEAK 0.862 —— 模型没问题，是门槛太高。已改 **0.65** 并重启，真人连续触发（162/166/168/173 行 wake，peak 0.716/0.689/0.734）。
- 顺带修掉两个观测/逻辑缺口：① `wake.py` 原来没有任何分数日志，「叫不应」与「麦克风坏了」无法区分 → 新增 3 s 节流 `[Wake] peak X / threshold Y`；② `_abort` 残留把下一轮录音砍成 0.3 s（`record_until_silence` 每 chunk 查 abort，而 `clear()` 只在录音之后的 `_process_request`）→ `_on_wake` 录音前显式 `_abort.clear()`，复测完整链路（Speech detected rms=0.0432 → 转写 → 回复）。
- 当前 jarvis = **job pwsh-38**（阈值 0.65 + 分数日志 + abort 清零 + 上一批 STT 语言/转录守卫/_tool_report）；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。要更灵敏就设 0.60，别再回 0.75。
