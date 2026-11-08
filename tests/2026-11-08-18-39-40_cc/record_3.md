# 轮 3：连续 5 轮对话触发压缩 + TTS（2026-11-08-18:47）

- 场景：node WS 连发 5 条 chat（记住 11/12/13 → 复述 → 总结），窗口跨过 `summarize_after=8` 触发 `_compress_oldest()`，验证 500 修复在 main 上生效。
- 期望：5 条 response 全出、无 500、无 Ollama 回落；TTS 出声。
- 实际：**5 条 response 全出**：`Done.` / `收到。我已记住数字 11 和 12。` / `收到。我已记住数字 11、12 和 13。` / `我说过数字：11、12、13。` / `总结：您请求我记住数字 11、12、13，并询问我曾记住哪些数字，最后要求我用一句话总结对话。`（第 5 条是真实摘要输出 → `llm.py` 的 `chat_template_kwargs` + `timeout=90` 在 main 上生效）；日志无 500、无「主模型失败」。`POST /tts`（:9880）→ **200 / 258,604 B / RIFF**。
- 结果：**PASS**
- 副作用披露：本轮测试真机执行了工具——`write_file` 在仓库根写 **`love_silvia.txt`（60 B，18:44:43）**、`type_text` 打字（11 / 11,12,13 / 摘要句）、`click_at(0,0)` 与 `scroll_screen`。该文件未 commit（测试产物）。
