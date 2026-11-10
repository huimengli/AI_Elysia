# 轮 2 — v0.6 特征、抗干扰混合与训练（2026-11-10 22:28–22:33）

- 时间：2026-11-10 22:28–22:33（`_t2_v06_noisy_clips.py`、`_t2_v06_features.py`、`openWakeWord/train_config_v06.yaml`、`_t2_train_cn.py`；job pwsh-114/116，日志 `.tmp\bats\v06noisy.log`、`v06feat.log`、`v06train.log`）
- 场景：13 条真人呼唤与噪声池（24 文件）按 SNR −5/0/5/10 dB 混合（seed 42，编号 121x，52 条，全部写入 **positive_***——方向纠正：上一批把带噪真呼唤当负样本）；另加 8 条定标纯噪声窗口（RMS 1994/1121/630/355，按真呼唤 RMS 1121 的 10^(SNR/20) 定标，不含语音）作 FP 抵抗负样本；特征走既有流式滑窗管线（prefix 53、NFR 24、1 s 零填充、chunk-boundary last-24 帧），真人 `*_120x` 行 ×5、带噪 `*_121x` ×2，与 **v0.3 合成特征**（不是 v0.4/v0.5）合并
- 期望：真人正样本行数显著上升（上一批 24 行是失败主因）；`steps 2500`、`max_negative_weight 1`（HB-021/027）导出 `aili_xiya_v0.6.onnx`
- 实际：行合并 = 正 24000 + 1195 → **25195**、正验收 4800 + 444 → 5244、负 57600 + 96 → 57696、负验收 4800 + 96 → 4896；训练 2500 步完成并导出 `aili_xiya_v0.6.onnx`（13,735 bytes），训练自带指标 `Final Model False Positives per Hour: 0.0`（目标 0.2/hour），tflite 转换照旧跳过（`onnx_tf` 缺）
- 结果：**PASS（数据与训练环节达标）**——真人正样本从 2 条→13 条、真人特征行 24→1195，训练一次成功无异常
- 备注：`_t2_v06_clips.py` 的「低分区」函数保留（`LOW_SCORE 0.25`、`MIN_LOW_LEN 0.8`），本录音返回 0 段；明日补录若含真实安静段，该函数会自动产出干净静音负样本
