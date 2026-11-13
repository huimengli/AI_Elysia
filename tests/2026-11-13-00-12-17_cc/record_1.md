# 验证轮 1 — 设置返回 3 个可切换唤醒模型与各自推荐阈值

- **时间**：2026-11-13 11:03
- **场景**：`GET /api/settings`（服务 `:7860` 现役，`curl.exe --ssl-no-revoke -s -m 20`，零截图）
- **期望**：`wake_model_options` 恰好 3 项，且**只有 Git 里跟踪的 3 个模型**（v0.3 / v0.9 / v1.0c），每项带推荐阈值（0.70 / 0.75 / 0.72）与 `current` 标记；`wake_word.threshold` = 现役 0.75
- **实际**：
  ```
  v0.3（2026-10-17 PASS：recall 0.94 / fp 0.09，推荐阈值 0.70） | aili_xiya_v0.3.onnx | thr=0.7 | current=False
  v0.9（现役，推荐：14 次件 12 / 近音 fp 6 / 对抗 4 / 环境音 0，阈值 0.75） | aili_xiya_v0.9.onnx | thr=0.75 | current=True
  v1.0c（音节窗约定：判别轴首次达标 fp 1 / 对抗 3 / 定标与环境 0，召回塌，可用区间 0.70-0.72，推荐 0.72） | aili_xiya_v1.0c.onnx | thr=0.72 | current=False
  wake_word.threshold = 0.75
  ```
- **结果**：**PASS**。3 项、只列 Git 里的模型、阈值与 `ai_buckup/onnx_opinion.md` 表 3 一致，`current` 正确指向现役 v0.9。
- **备注**：`config.yaml` 新增 `wake_word.model_options`（3 条，含 label / model 绝对路径 / threshold），`web.py` GET 由 `model_options` 生成 `wake_model_options`；未入 Git 的 v1.0 / v1.0b / v1.1 **没有**出现在列表里。
