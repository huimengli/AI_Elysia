# 验证轮 3 — 窗口里的服务真的起来了（三端口 + 四灯 health）

- 时间：2026-11-09 21:37–21:38（`.tmp\bats\run37.bat` → `launch2.log`）
- 场景：第 2 轮由脚本弹出的两个 cmd 窗口（pid 21056 / 18696）加载模型 60–120 s 后，采集监听端口、进程表与 `GET /api/health`。
- 期望：`:7860` 与 `:9880` 由**脚本启动的新进程**监听，`:8080` 仍在；四灯（wake/asr/llm/tts）全部 `online: true`。
- 实际：
  ```
  TCP  0.0.0.0:7860  LISTENING  4920   (python.exe, 父窗口 pid 18696)
  TCP  127.0.0.1:8080 LISTENING 13808  (llama-server.exe)
  TCP  127.0.0.1:9880 LISTENING 7028   (python.exe, 父窗口 pid 21056)
  ```
  health（原文摘录，中文部分照原样）：
  ```json
  {"wake":{"online":true,"listening":true,"model":"aili_xiya_v0.3.onnx","threshold":0.65,
           "score":0.072,"peak":0.159,"last_detect":"21:37:48"},
   "asr":{"online":true,"warm":true,"model":"small","language":"zh","device":"cpu"},
   "llm":{"online":true,"provider":"llamacpp","url":"http://127.0.0.1:8080/v1"},
   "tts":{"online":true,"provider":"gptsovits","url":"http://127.0.0.1:9880/tts"}}
  ```
- 结果：**PASS**（脚本开出的窗口确实把 GPT-SoVITS 和 Jarvis 拉起并监听；`asr.warm=true` 说明 whisper 已常驻；唤醒在上一个 3 s 窗口内出现峰值 0.159 并在 21:37:48 触发过一次）
- 备注：第 4 个「Jarvis Status」窗口每 5 s 打印 8080/9880/7860 的监听 pid 与 health 文本，是「三个或更多 cmd 界面」里的第 4 个；不需要时可自行关闭，不影响服务。全程零截图（`netstat`/`tasklist`/`curl` + 窗口标题）。
