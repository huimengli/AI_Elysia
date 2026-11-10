# 批次结论 · 2026-11-09-21-55-14（阈值 0.7 + 唤醒音直放 + 工具名汉化）

**3/3 PASS**（验证轮，零截图，全部用 `netstat`/`curl`/日志/WS 事件取证）

| 需求 | 改动 | 证据 | 结果 |
| --- | --- | --- | --- |
| ① 触发阈值 0.7 | `config.yaml` `wake_word.threshold: 0.65 → 0.7`（逻辑无硬编码，`state` 与灯都取该值） | `.tmp\bats\h6.log` / `h7.log` 的 `wake.threshold 0.7`；真人实测 `peak 0.773 ≥ 0.7` 成功触发、底噪峰值 0.25–0.62 均不触发（`.tmp\jarvis3.log` 的 `[Wake] peak` 行） | PASS |
| ② 唤醒音太快 | `preload_ack_audio()` 启动时把 5 条应答音解码进内存 + `_output_stream()` 常驻复用同一输出流，唤醒后只写流；首字延迟 ≈20 ms | `ack2.log`（发现 `latency="small"` 抛 `TypeError`）、`ack3.log`（预热 3125 ms 后 `ack stream ready 0 ms`，2.26 s 音频 total 2281 ms）、真人唤醒 `ack stream ready in 0 ms / total 2069 ms`（`.tmp\jarvis3.log:7-10`） | PASS |
| ③ 工具名汉化 | `TOOL_LABELS` 33 项 + `tool_label()`；`_tool_report` 与 4 处广播带中文 `label`；`index.html` 显示用 `msg.label \|\| msg.name` | `tool1.log`（33/33 无遗漏，文案 `我执行了 输入文本、按下按钮：OK enter`）、`ws1.log`（真人网页触发：`["tool","get_time","看时间"]`、`["tool_result","get_time","看时间"]`） | PASS |

结论：三项需求都按「不新增网络调用、不新增模型推理」的思路实现——阈值只是配置、唤醒音走内存直放（彻底绕过 TTS 合成）、汉化是一张静态映射表。英文工具名保留在事件与协议里，检索与 LLM schema 不受影响。

修掉的两个真实缺陷（本轮内发现并修复）：
1. `sd.OutputStream(latency="small")` 在装的这版 sounddevice 会抛 `TypeError: must be real number, not str` → 去掉该参数；
2. 只缓存 PCM 不够：建流成本 3125–3444 ms，若留在唤醒时才付，**第一次**唤醒仍然慢 3.4 s → 改为启动时预热建流（`output stream warmed in 2868 ms`），使第一次唤醒也 ≈20 ms。

遗留（登记，未改）：真实语音轮里 STT 两次 `ConnectError WinError 10054`（`.tmp\jarvis3.log:19-23`）、`asr.warm=false`，以及 VAD 在噪声下录满 30 s 上限。建议另开需求（`stt` 侧）处理。
