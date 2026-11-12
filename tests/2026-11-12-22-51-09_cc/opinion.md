# 批次结论 tests/2026-11-12-22-51-09_cc（Q17 裁决 C：sherpa 能量门 + 3 轮 A/B）

## 1. 实现

`jarvis/stt.py` 新增 `_energy_gate(audio, sample_rate, threshold, window_ms, mode)`，在 sherpa 分支前调用（whisper 分支的 `vad_filter=True` 不变）：

- `mode="span"`（最终采用）：100 ms 窗算 RMS，找第一个/最后一个 voiced 窗，**只掐头尾静音**、保留中间全部内容，前后各留 100 ms；全静音时返回原数组（不制造空输入）；
- `mode="concat"`（第 1 轮的写法，已否决）：只保留 voiced 窗并拼接；
- config 键：`stt.sherpa.energy_gate`（默认 true）、`stt.sherpa.energy_threshold`（最终默认 **0.008**）、`stt.sherpa.energy_mode`（默认 `span`）；
- 探针 `training/_t2_asr_ab_gate.py`（入 Git）：三配置对照（whisper 现役 / sherpa 无门 / sherpa 能量门），已知文本集 6 件（文件名即真值，sim 判据 ≥0.8）+ 真实麦克风抓取 `.tmp/capture_*.wav` ≥3 s 前 12 条。

## 2. 3 轮结果

| 配置 | 已知集 sim ≥0.8 | 乱码/空件（18 件） | 总耗时（18 件） |
| --- | --- | --- | --- |
| whisper 现役 | **3/6** | 9 | 34087-36911 ms |
| sherpa 无门（基线） | 2/6 | 1 | 10847-11781 ms |
| concat + THR 0.015（第 1 轮） | 1/6 ↓ | 4 ↑ | 6462 ms |
| span + THR 0.015（第 2 轮） | 1/6 ↓ | 2 | 7388 ms |
| **span + THR 0.008（第 3 轮）** | **2/6** | **0** ✓ | **5308 ms** ✓ |

## 3. 结论

1. **「逐窗拼接」不是 VAD 跳过，是音节切碎**：100 ms 窗会在轻声/擦音中间切，第 1 轮 5 件里 4 件 sim 下降、2 件归零（`米希雅`→「对呀」、`爱丽丝`→「还一个」）→ 否决 concat，改只掐头尾静音（span）。
2. **门限必须低**：0.015 在 span 下仍切掉轻声音节（`电视机`→「电脑」、`米希雅` 整件没）；0.008 复原全部已知件，并让乱码归零（0 件）、耗时减半（5308 ms vs 无门 10847 ms，8 条 30 s 无声件从 627-868 ms 降到 26-40 ms）。代码默认已定为 `span / 0.008`。
3. **sherpa 的天花板不在静音**：已知集 sim 停在 2/6（whisper 3/6），瓶颈是 Paraformer 对近音的声学判别（爱莉希雅→爱丽西雅 / 艾丽安娜 / 泰利西亚），与静音无关 → **`stt.engine` 保持 whisper，`config.yaml` 未改**。
4. 能量门是**可用组件**：速度、静音鲁棒性、长句上下文三项都改善；日后若切 sherpa 或做 VAD 前置判断可直接用。`need_user.md` Q7 的 A/B 结论（whisper 优先）未被推翻，只是把「sherpa 加能量门后重跑 3 轮」这条待办做完并结案。

## 4. 环境类事实

- 探针第一次跑缺 HF 环境变量 → faster-whisper 去 Hub 下载报 `LocalEntryNotFoundError`（`WinError 10054`）；必须带 `HF_ENDPOINT=https://hf-mirror.com`、`HF_HOME=<repo>\.hf-cache`、`HF_HUB_DISABLE_XET=1`；打分前停掉 `:7860/:8080/:9880`（虚拟内存），跑完重启 + 4 灯复核。
