# 第 2 轮 · 录音落盘 + ASR 参数 A/B（合成语音 3/3、真人 1 句）

- 时间：2026-11-10 18:00–18:16（`.tmp\bats\asr1.log`、`ab1.log`、`.tmp\jarvis6.log`）
- 改动：`jarvis/stt.py` 新增 `_dump_audio()`（每次录音写 `.tmp\capture_<ts>.wav`，16 kHz 单声道，`.gitignore` 内不 commit）与 `_trim_leading_silence()`；`transcribe` 参数由 `beam_size=5` 改为可配置 `beam_size=10 / best_of=5 / vad_filter=True / condition_on_previous_text=False / initial_prompt=<简体中文+项目词表>`（config.yaml 新增对应键）
- 期望：① 录音可离线复现（做 A/B 的前提）；② 新参数在中文短句上至少不劣于旧参数，并消除繁体

## A/B ①（合成语音，`.tmp\bats\asr1.log`）

用 GPT-SoVITS 合成 3 句作为已知文本的对照（真人不可控时的可复现替代）：

```
目标=你能看得见屏幕吗？  旧参数=你能看得見屏幕嗎   新参数=你能看得见屏幕吗?
目标=现在几点了？        旧参数=现在几点了        新参数=现在几点了?
目标=把音量调到二十。    旧参数=把音量調到20       新参数=把音量调到二十。
```

- 结果：**3/3 PASS** —— 旧参数全部繁体/丢标点（`看得見屏幕嗎`、`調到20`），新参数逐字正确且带标点

## A/B ②（真人麦克风，`.tmp\bats\ab1.log`）

```
file=.tmp\capture_1794305716.wav dur=4.8s rate=16000 peak=0.1178 rms=0.0104
A 旧参数(beam5,无prompt,无VAD,不裁剪) = 你看得见吗?
B 新参数(裁剪+beam10+VAD+prompt)      = 你看得见吗?
C 新参数不裁剪                        = 你看得见吗?
D 裁剪+beam10+VAD 无prompt            = 你看得见吗?
E 裁剪+beam10+无VAD+prompt            = 你看得见吗?
F 新参数+2x增益                        = 你看得见吗?
```

- 结果：**部分 PASS** —— 落盘成功（`[STT] capture saved: capture_1794305716.wav (4 s)`）、VAD 正常收尾、新参数不再出繁体；但真人说的「你能看得见屏幕吗？」在 6 种参数组合下都只识别成 `你看得见吗?`（丢「能」「屏幕」）
- 关键发现：真人录音 `peak 0.1178 / rms 0.0104`，`+2x 增益` 结果不变 → 问题不在电平，而在**采集清晰度/whisper small 对中文短句的鲁棒性**；换引擎（sherpa-onnx paraformer-zh）是唯一可能显著改善的路径，已写入 `need_user.md` Q7 等用户授权
- 另一发现（登记，未改）：18:03 那次 `peak 0.736 / 0.799` 在 0.7 阈值下触发唤醒，随后 30 s 录满、转写为空 —— 说明 0.7 阈值下仍有环境误触发，`record_until_silence` 缺少「无人说话就快速退出」的机制
