# 第 3 轮：Jarvis「看屏幕」演示 —— 用浏览器快照读 4 盏灯（2026-11-12 23:53）

- 时间：2026-11-12 23:53
- 场景：`browser_find`（正则 `/唤醒|识别|音量|LLM|TTS|灯/`）在页面上定位 4 盏健康灯，`browser_console_messages(level=error)` 复核页面错误，最后 `browser_close`
- 期望：不截图就能读到灯名与 detail，与 `/api/health` 一致
- 实际（快照里的灯，含 tooltip 文本）：

| 灯 | detail（快照文本） |
| --- | --- |
| **唤醒** | `aili_xiya_v0.9.onnx / threshold 0.75 / peak 0.422 / 上次触发 23:51:46` |
| **语音识别** | `faster-whisper small / cpu / zh（模型已加载=True）` |
| **LLM** | `llama.cpp (Local) @ http://127.0.0.1:8080/v1` |
| **TTS** | `GPT-SoVITS @ http://127.0.0.1:9880/tts` |

同时读到状态标签「待命中」「思考中」。与 `curl.exe --ssl-no-revoke -s -m 20 http://127.0.0.1:7860/api/health` 的 4 灯全 online 一致（peak 0.422 是页面刷新后的最新值）。

- 结果：**通过** —— 「看屏幕」能力成立，且全程零截图（可访问性快照 + `browser_find`）。
- 备注：console 唯一错误仍是 favicon 404（良性）；`browser_close` 后无残留标签页。
