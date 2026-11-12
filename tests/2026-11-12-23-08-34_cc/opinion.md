# 批次结论 tests/2026-11-12-23-08-34_cc（未完项 1：「我没听清，请再说一遍」入 RAM 应答池 + hot_phrases 小表）

## 1. 实现

- **预合成 + 具名应答池**：`jarvis/data/ack/ack_no_heard.wav`（现役 `:9880/tts` 预合成，3.32 s @ 32 kHz，与现有 5 条同目录同格式）；`jarvis/tts.py`：
  - `preload_ack_audio()` 把整目录 wav 载入 RAM，并**统一采样率**（重采样到目录里最常见的采样率）——不统一的话第一次播 32 kHz 具名句要重开输出流，实测 ~3.4 s，T8 的「缓存 PCM + 复用同一条输出流」提速就白丢了；
  - 具名缓存 `_ack_named[文件名去扩展名] = (audio, rate)` + `play_ack_phrase(name)`；抽出共用 `_play_cached()`，打断/`stop_speaking()`/`_speaking` 语义与 `play_ack_wav()` 完全一致；`play_ack_wav()` 轮播行为不变。
- **接线**：`jarvis/main.py` 新增 `_ask_repeat_if_unmuted()`——先具名 ack，缓存缺该句才回退 live TTS；**只在** `Transcription empty` 与 `Low-quality transcription` 两个分支调用（不是每次唤醒都播）。
- **热词小表**：`jarvis/memory.py` 在既有 `memory.db` 加 `hot_phrases(text, kind, count, first_seen, last_seen)`，`kind` ∈ `user`/`hot`/`near_miss`，`count` 累加（上限 1000）、行数上限 `_HOT_CAP=200`（超出淘汰低 count），时间戳用 AGENTS 格式 `yyyy-MM-dd-HH-mm-ss`；写入点 = 真实转录成功后的整句（`user`）+ 与「爱莉希雅」difflib 相似度 0.5-0.9 的近音句（`near_miss`）；`jarvis/stt.py` 的 `set_hot_words()` / `_bias_prompt()` 是偏置入口，`config.yaml` 新增 `stt.hot_bias`（**默认 false**）。

## 2. 3 轮结果

| 轮 | 判据 | 结果 |
| --- | --- | --- |
| 1 具名池 | 6 clip 载入 + 统一 32000 Hz、具名句可播、打断后 `is_speaking=False` | ✓（3 轮 `play_ack_phrase` 3330/3300/3330 ms，流就绪 0 ms；打断清队列 1219 ms） |
| 2 分支接线 | empty/lowq 播具名句、normal 不播、唤醒应答仍是轮播 ack | ✓（`['轮播 ack','具名 ack[ack_no_heard]']` ×2；normal 只轮播） |
| 3 表 + 偏置 A/B | 表行为（写入/累加/上限 200）✓；偏置后 sim ≥0.8 计数 ≥ A 且逐件不变差 | **偏置判据不通过**：计数 3/6 → 3/6，长句 ↑（0.92→0.96、0.83→0.86）但**短句被吸附**（爱丽安娜 0.75→0.67、爱丽丝 0.33→0.29、米希雅 0.57→0.50，变差 3 件），总耗时 23125→81531 ms（含一次 61.8 s 转录失控）；`HOT_BIAS=0` 时 B 与 A **逐件完全一致**（变差 0） |

## 3. 结论

1. **应答句已进 RAM 池并接对分支**：空转录与低质量转录播「我没听清，请再说一遍」（无 TTS 往返，出声 = 句长 3.3 s），非唤醒时不播，barge-in 语义不变。
2. **hot_phrases 表留下，作为数据源**（统计 + 训练/验收导出 `near_miss`，与 Q13 的「真人近音负样本」来源同一）；**whisper 的 `initial_prompt` 热词偏置默认关闭**——whisper 对短音频的 prompt 吸附太强，会把 2-3 字近音件直接写成热词（`爱丽丝`→「爱莉希。」），这比它带来的长句改善（2 件 +0.03/+0.10）代价大；`stt.hot_bias: false` 已写进 `config.yaml`，要开需显式改。
3. **探针必须只测目标路径**：第一次跑 `lowq` 注入「嗯」被判据当作「能理解」，于是真跑 LLM/TTS 并**真打开了 Edge**，把 `:8080`/`:9880` 压死；低质量件必须用**无 CJK 且 ≤20 字符**的退化输出（`records/2026-11-08-18-54-18.md` 的 literal `You`），`_process_request` 也要 stub。
4. 探针用**每次独立的临时 sqlite**，不写现役 `memory.db`（第一轮造 210 条 filler 挤掉真实热词，已清理）；`record_phrase` 形参不能叫 `text`（遮蔽 sqlalchemy `text()`）。
