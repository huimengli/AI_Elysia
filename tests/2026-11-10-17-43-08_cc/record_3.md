# 第 3 轮 · 重启后 WS 端到端：工具名与结果全中文、协议字段仍英文

- 时间：2026-11-10 18:19（`.tmp\bats\ws3.log`），Jarvis 已带新代码与 HF 环境变量重启（`.tmp\jarvis6.log` 前 8 行：`ack audio preloaded: 5 clips` / `Loaded small on cpu` / `whisper warmed in 2831 ms` / `output stream warmed in 2760 ms`）
- 场景：`.tmp\probe_ws.py` 连 `ws://127.0.0.1:7860/ws` 发「现在几点了？用一句简体中文回答」，抓 `tool` / `tool_result` 事件与最终应答；同时 `Invoke-WebRequest` 取 `/api/health`（`.tmp\bats\h9.log`）
- 期望：`label` 中文、工具结果中文、`name` 保持英文（协议不变）、四灯在线
- 实际：

```
first={"type": "connected", "message": "爱莉希雅已上线。"}
tool_events=[["tool", "get_time", "看时间"], ["tool_result", "get_time", "看时间"]]
final=现在是晚上 6 点 18 分，星期二。

asr: {"online":true,"warm":true,"model":"small","language":"zh","device":"cpu"}
wake: threshold 0.7, listening true
llm: llama.cpp (Local) @ :8080 在线 | tts: GPT-SoVITS @ :9880 在线
```

- 结果：**PASS** —— 中文 label（`看时间`）、结果文本中文（`2026-11-10 18:1x:xx 星期二`）、事件里的 `name` 仍为英文 `get_time`；本轮应答的星期也是 `星期二`（与 `get_time` 一致，上一批的「星期五」问题未复现）
- 备注：本轮证明「结果文案汉化」与协议层解耦；后续真人语音轮的中文播报汉化会随结果文案一起变（`我执行了 看时间：…`）
