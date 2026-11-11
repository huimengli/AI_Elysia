# 轮 2 — v0.7 训练与部署管线矩阵（配比失衡，未通过）（2026-11-11 20:47–20:53）

- 时间：2026-11-11 20:47–20:53（`.tmp/_t2_v07_features.py` → `openWakeWord/train_config_v07.yaml` → `_t2_train_cn.py`，日志 `.tmp\bats\v07feat.log`、`v07train.log`、`v07matrix.log`）
- 场景：新 8 件 clip 走 `_t2_stream_features_v02` 流式滑窗（prefix 53 / NFR 24，与 `predict_clip` 一致，HB-027），与 v0.6 特征（v0.3 合成对抗 + 13 次真人呼唤 + 带噪呼唤）合并：正样本行 ×3、真人近音负样本行 **×5**；2500 步、`max_negative_weight: 1`
- 期望（判据，records/2026-11-11-20-34-04.md）：13 次呼唤检出 ≥ v0.6(10)、真人近音 fp 尽量 0、带噪呼唤检出 ≥、环境音 ≤1、定标纯噪声 0
- 实际（部署管线，1280 chunk、检出后 reset、2 s 冷却，阈值 0.7）：
  - 13 次呼唤 36.12 s：v0.7 检出 **5**（v0.6 = 10）→ 灵敏度掉了 5 次
  - 新录音 tv 2 / browser 1 / hello 1 / music 1 / faint 1（v0.6 2/2/1/2/1）
  - **真人近音 fp 仍 2**：ailianna 1（max 0.712）、aisli 1（max 0.732）、mixiya 0
  - 定标纯噪声 0、合成对抗 3、环境音 0
  - 训练日志 `Final Model False Positives per Hour: 0.0`（该指标只看 val_fp，不反映真人近音）
- 结果：**FAIL**（召回显著下降、近音 fp 未改善）
- 备注：负样本行重复 ×5（整件 5.8/5.7 s，语音密集）压过正样本行，模型学会「语音密集=拒绝」。教训：**行重复比就是灵敏度旋钮**，真人负样本不能一上来给 ×5
