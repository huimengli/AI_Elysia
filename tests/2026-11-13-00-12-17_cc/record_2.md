# 验证轮 2 — PUT 切到 v1.0c + 0.72，**不重启**即刻生效

- **时间**：2026-11-13 11:03
- **场景**：`PUT /api/settings`，body `{"wake_word":{"model":"...aili_xiya_v1.0c.onnx","threshold":0.72}}`（curl，model + threshold **一起**提交）；6 s 后读 `/api/health`
- **期望**：`/api/health` 的 `model` = `aili_xiya_v1.0c.onnx`、`threshold` = 0.72，4 灯全 online 且 `listening` 仍为 True（换模型不断流）；日志出现重载行
- **实际**：
  ```
  PUT → {"status":"ok"}
  wake: {"online":true,"listening":true,"model":"aili_xiya_v1.0c.onnx","threshold":0.72,
         "score":0.481,"peak":0.606,"last_detect":"11:02:21"}
  lamps: wake=True listening=True asr=True llm=True tts=True
  日志尾部：
    [Wake] peak 0.417 / threshold 0.75
    [Wake] reloaded aili_xiya_v1.0c.onnx / threshold 0.72
    [Wake] peak 0.717 / threshold 0.72
    [Wake] peak 0.523 / threshold 0.72
  ```
- **结果**：**PASS**。新模型的分数确实来自新模型（0.717 与 0.523 是 v1.0c 的峰值量级，不是 0 缺省值），说明 `predictions` 的键名解析（`Path(...).stem` = `aili_xiya_v1.0c`）与 openwakeword 内部键一致；mic 流复用未中断。
- **备注**：重载后 2 s 冷却（`_ignore_until`）覆盖 Model() 的 1 s 随机播种 warmup（HB-032），换模型瞬间不会误触发；`config.yaml` 同批落盘。
