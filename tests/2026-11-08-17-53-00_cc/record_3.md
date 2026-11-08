# 轮 3：重启后 UI / API / TTS 健康检查（2026-11-08-18:02）

- 场景：`llm.py` timeout 改 90 后重启 jarvis（job pwsh-17），检查页面、三个 API、TTS 与一次 WS 对话。
- 期望：全部正常，链路无 500。
- 实际：`GET /` **200 / 42,420 B**（`<title>爱莉希雅</title>`、`--pink`、`petal`）；`/api/settings` 200（`active_provider: llamacpp`、tts gptsovits 完整）、`/api/providers` 200；`POST /tts`（:9880）→ **code=200 / 266,284 B / RIFF**；WS chat「用一句话说明你现在正常吗」→ `RESPONSE: 是的，我现在正常。系统运行良好，CPU 使用率较低（34%）…`，日志显示 `[Tool: get_system_info] CPU: 34% | RAM: 24.7/27.8 GB | Disk C: 0.3/200 GB free`，无 500。
- 结果：**PASS**
- 备注：C 盘剩余 **0.3 GB**（llama 日志报的 free），真人测试中请留意；`write_file` 工具对非白名单路径正常拒绝（`Path not in allowed list`）。
