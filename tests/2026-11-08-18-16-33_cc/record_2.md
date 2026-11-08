# 轮 2：main 版服务与 WS 连通（2026-11-08-18:22）

- 场景：main 代码（无 17:53 修复）下检查 `/api/settings` 与 WS `chat`。
- 期望：服务可用；并确认 main 缺修复的风险点。
- 实际：`/api/settings` 200（`active_provider: llamacpp`、tts gptsovits 完整）；node 原生 WS 连 `ws://127.0.0.1:7860/ws` → `connected: 爱莉希雅已上线。` → `status: 思考中…` → **RESPONSE「我是爱莉希雅，一位完全自主的个人 AI 助手。」**。
- 结果：**PASS**
- 备注：main 的 `main.py` 没有「前导 system 摘要并入唯一 system」的修复，`llm.py` 也没有 `chat_template_kwargs` 与 `timeout=90`（仍是 15 s）——真人测试若聊到 8 条触发压缩，`保存设置后管线报错`（8080 500 → 回落 Ollama）会在 main 上重现。
