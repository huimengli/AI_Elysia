# 轮 3：Web UI + WS 全链（:7860）（2026-11-08-17:34–17:40）

- 场景：`python -u -m jarvis.main`（env `HF_ENDPOINT/HF_HOME/HF_HUB_DISABLE_XET`），检查首页、API、WS 全链事件。
- 期望：`GET /` 200 且为 T6 的 Elysia 页；`/api/settings`、`/api/providers`、`/api/events` 正常；WS 发 `chat` 后收到完整事件序列与 response。
- 实际：`GET /` **200 / 42,420 B**，`<title>爱莉希雅</title>`、`--pink`、`petal` 均在；`/api/settings`（tts gptsovits + providers llamacpp/ollama + context）、`/api/providers`、`/api/events?limit=5` 均 200 JSON。node 原生 WebSocket 连 `ws://127.0.0.1:7860/ws` 发 `{type:'chat',text:'用一句话介绍爱莉希雅（15字内）'}` → **6 条事件**：`connected,user,status(思考中…),tool(type_text),tool_result,response(爱莉希雅是一位强大的AI助手。)`；`/api/events` 也落盘 `user(web)` + `assistant(web)`。
- 结果：**PASS**
- 备注：`tool type_text` 是真实副作用——它往 PC 打字（本次打到 harness 桌面）；真人测试前请留意。语音链路：17:33:04 wake 触发→30 s 录音→`STT cuda failed (CUDA driver version is insufficient) 回落 cpu，small on cpu 加载成功`→「Transcription empty — didn't catch anything」（当时无有效语音），wake 与 mic 通道本身可用。
