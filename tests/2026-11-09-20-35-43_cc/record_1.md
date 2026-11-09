# 验证轮 1 — 2026-11-09-20-35-43 唤醒灯（API 数据源）

- 时间：2026-11-09 20:59–21:04
- 场景：改完 `jarvis/wake.py` + `jarvis/web.py` 后重启 Jarvis（`:7860`，旧 pid 14604 被杀，新进程由 `.tmp\bats\run28.bat` 拉起），用 `curl http://127.0.0.1:7860/api/health` 取四灯数据（全程文本通路，零截图，输出转 UTF-8 到 `.tmp\bats\h5u.log`）
- 期望：`/api/health` 返回 4 项，`wake` 排在最前，`online/listening/model/threshold/score/peak/last_detect` 齐备，且其余三灯不回归
- 实际：
  ```
  {"wake":{"online":true,"listening":true,"model":"aili_xiya_v0.3.onnx","threshold":0.65,
          "score":0.154,"peak":0.154,"last_detect":"21:03:00",
          "detail":"aili_xiya_v0.3.onnx / threshold 0.65 / peak 0.154 / 上次触发 21:03:00"},
   "asr":{"online":true,"warm":true,"model":"small","language":"zh","device":"cpu",...},
   "llm":{"online":true,"provider":"llamacpp","url":"http://127.0.0.1:8080/v1",...},
   "tts":{"online":true,"provider":"gptsovits","url":"http://127.0.0.1:9880/tts",...}}
  ```
- 结果：**通过**
- 备注：
  - `key` 顺序即 `wake → asr → llm → tts`，与 UI 灯序一致；
  - `listening:true` 说明麦克风在唤醒线程手里（未在 STT 录音窗口内）；
  - `last_detect 21:03:00` 是重启后**真实的一次唤醒触发**，证明状态写入链路通（不是默认 0）；
  - `score/peak 0.154` 为最近一个 3 s 日志窗口内的峰值，低于 0.65 阈值 → 未触发，符合预期；
  - `asr.warm` 本轮已为 `true`（上一批次为 `false`），说明重启后 whisper 已常驻；
  - `llm/tts` 保持 `online:true`，无回归。
