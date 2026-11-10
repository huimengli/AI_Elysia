# 第 1 轮 · 唤醒阈值 0.7 落地并生效

- 时间：2026-11-10 16:38–16:44（需求提出于 2026-11-09 21:55:14，跨到次日执行）
- 场景：`config.yaml` `wake_word.threshold` 0.65 → 0.7；`start_all.bat` 全量启动三服务（`cmd /c` 通道，子窗口继承重定向管道所以父进程不退出，属通道特性，双击使用不受影响），Jarvis 以新代码重启
- 期望：`GET /api/health` 的 `wake.threshold` 为 **0.7**；`wake.online/listening` 正常，唤醒灯详情同步显示新阈值
- 实际（`.tmp\bats\h6.log`，16:44 采集）：

```json
{"wake":{"online":true,"listening":true,"model":"aili_xiya_v0.3.onnx","threshold":0.7,
 "score":0.253,"peak":0.497,"last_detect":"16:42:34",
 "detail":"aili_xiya_v0.3.onnx / threshold 0.7 / peak 0.497 / 上次触发 16:42:34"}}
```

- 端口实测（同刻 `netstat`）：`:7860` pid **15820**（python，`jarvis.main`）、`:8080` pid **8392**（`llama-server.exe`）、`:9880` pid **9420**（python，`api_v2.py`）全部 LISTENING
- 结果：**PASS** — 新阈值 0.7 由重启后的进程实际读出并广播（`state["threshold"]` 取自 config，无硬编码）
- 备注：`asr.warm=false`（whisper 尚未常驻，`device: cuda`）；`peak 0.497 < 0.7` 说明当前麦克风底噪/自回声在新阈值下不会触发，正是把阈值提高到 0.7 的目的（v0.3c 验收：0.7 → recall 0.94 / false-positive 0.09）
