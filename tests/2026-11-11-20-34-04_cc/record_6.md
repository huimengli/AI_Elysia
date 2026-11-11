# 轮 3 — v0.8 配比修正、阈值扫描与打分非确定性（2026-11-11 20:55–21:12）

- 时间：2026-11-11 20:55–21:12（`.tmp/_t2_v08_features.py` → `openWakeWord/train_config_v08.yaml` → `_t2_train_cn.py`；日志 `.tmp\bats\v08feat.log`、`v08train.log`、`v08train2.log`、`v08train3.log`、`v08matrix.log`、`v08sweep75.log`、`v08sweep80.log`、`v06determinism.log`）
- 场景：沿用同一批 clip，行重复改为正样本 ×5、真人近音负样本 ×3；3000 步、`max_negative_weight: 1`。首次两次训练失败（`positive_test` 缺 wav → HB-028 已知；补齐后一次因内存峰值 `DefaultCPUAllocator: not enough memory` 失败），第三次成功，`Final Model False Positives per Hour: 0.0`
- 期望：同轮 2 判据（13 次呼唤 ≥10、真人近音 fp 0、合成对抗 ≤4、环境音 ≤1）
- 实际（部署管线阈值 0.7）：v0.8 = 13 次呼唤 **12**（v0.6 = 10）、新录音 tv 2 / browser 2 / hello 1 / music 2 / faint 1（v0.6 2/2/0/2/1）；**真人近音 fp = 3/3**（ailianna 0.703、aisli 0.789、mixiya 0.723）；定标纯噪声 0、合成对抗 **6**（>4）、环境音 1
- 阈值扫描：
  - 0.75：v0.8 → 13 次 8、新录音 7 次、近音 fp 0、合成对抗 **6**、环境音 0；v0.6 → 13 次 5、近音 fp 0、合成对抗 2、环境音 0
  - 0.80：v0.8 → 13 次 3、近音 fp 0、合成对抗 3；v0.6 → 13 次 1、近音 fp 0、合成对抗 2
- 关键新发现（`.tmp\bats\v06determinism.log`，同一音频、同一模型、3 次独立实例）：
  - ailianna max = 0.753 / 0.730 / 0.732（≥0.7 的 chunk 数 7/4/4）
  - aisli max = 0.681 / 0.713 / 0.671（0/1/0）
  → `AudioFeatures` 用 `np.random` 噪声初始化特征缓冲，warmup 前缀使逐 chunk 分数每次漂移 ±0.02–0.07。**贴近阈值的单次测量不可信**，边界样本必须多轮复测
- 结果：**FAIL**（v0.8 召回最高，但真人近音 fp 与合成对抗都超判据；阈值 0.75 时合成对抗 6 仍 >4）
- 备注：三次训练的 `Final Model False Positives per Hour` 都是 0.0，**该指标只看 400 条 val_fp 合成样本，完全反映不出真人近音负样本**——以后验收必须以部署管线矩阵为准（已记 hard_bug.md HB-032）
