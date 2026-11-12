# 第 2 轮：空转录 / 低质量转录分支接具名 ack（2026-11-12 23:10-23:25）

- 时间：2026-11-12 23:23
- 场景：`jarvis/main.py` 新增 `_ask_repeat_if_unmuted()`（先 `play_ack_phrase("ack_no_heard")`，缓存缺句才回退 live TTS），`Transcription empty` 与 `Low-quality transcription` 两个分支改用它；探针 `training/_t2_wake_empty_probe.py` 把录音/转录/播放/广播 monkeypatch，跑 `handle_wake()`，三种 MODE
- 期望：`empty` 与 `lowq` 播具名句；`normal` **不播**；唤醒时的轮播 ack 仍播一次
- 实际（3 个 MODE 各 1 次，共 3 次运行）：

| MODE | 转录注入 | 播放序列 | 判据 |
| --- | --- | --- | --- |
| empty | `""` | `['轮播 ack（唤醒应答）', '具名 ack[ack_no_heard]']` | 该播 → **True** ✓ |
| lowq | `"you"`（无 CJK、≤20 字符，`_looks_understandable` 为假） | `['轮播 ack（唤醒应答）', '具名 ack[ack_no_heard]']` | 该播 → **True** ✓ |
| normal | `爱莉希雅，帮我打开浏览器` | `['轮播 ack（唤醒应答）']` | 不该播 → **True** ✓ |

- **第一次跑的教训（已修正）**：`lowq` 原本注入「嗯」，但 `_looks_understandable` 对含 CJK 的文本一律算「能理解」，于是探针走进完整对话管线，**真调 LLM、真调 TTS、真开了 Microsoft Edge**，并把 `:8080`/`:9880` 压死（llama-server 退出码 3762504530、api_v2.py 退出码 1）。修正 = 低质量必须用无 CJK 且 ≤20 字符的退化输出（`records/2026-11-08-18-54-18.md` 实测的 literal `You`），并把 `_process_request` 也 stub 掉（探针只测应答路径，不跑 LLM/工具）。
- 结果：**通过** —— 只在空转录与低质量转录播该句，唤醒应答仍是轮播 ack，非唤醒时不播。
- 备注：零截图；服务在探针后需重启（第 4 步 4 灯复核）。
