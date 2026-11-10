# 第 3 轮 · 重启后 WS 链路与中文工具名无回归

- 时间：2026-11-10 17:35（`.tmp\bats\ws2.log`）
- 场景：用 `.tmp\probe_ws.py` 连 `ws://127.0.0.1:7860/ws` 发一条聊天（`现在几点了？用一句简体中文回答`），抓 `tool` / `tool_result` 事件与最终应答
- 期望：连接、工具事件（带中文 `label`）、应答齐全；重启与 STT 预热不影响上一批已验收的四灯/中文播报
- 实际：

```
first={"type": "connected", "message": "爱莉希雅已上线。"}
tool_events=[["tool", "get_time", "看时间"], ["tool_result", "get_time", "看时间"]]
final=现在是 2026年11月10日 星期五 17:35。
```

- 结果：**PASS**（链路侧）—— 连接、工具事件、`label` 中文（`看时间`）、应答均在；四灯（`wake 0.7 / asr warm=true / llm / tts`）同刻 health 全在线
- 备注：应答里「星期五」仍是 2B 模型的日期问题（`tool_result` 里是 `星期二`）——与 ASR 无关，已在 `record_2.md` 与 record 中登记为 LLM 侧遗留
