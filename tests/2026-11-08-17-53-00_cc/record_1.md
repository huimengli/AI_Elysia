# 轮 1：复现「保存设置后管线报错」根因（2026-11-08-17:55）

- 场景：真人测试中两次 wake 后 `[WARN] Primary provider failed (Error code: 500 … Jinja Exception: System message must be at the beginning)` → 回落 Ollama（未运行）→ `Pipeline error: Failed to connect to Ollama`。直接对 `:8080` 做三组 messages 探针（带 `chat_template_kwargs.enable_thinking=false`）。
- 期望：定位触发条件（是否第二条 system 消息）。
- 实际：A `[system,user]` → 正常出 content；B `[system, system('[Earlier context: 聊过天气]'), user]` → **exit 0 但 body 是 500**：`While executing CallExpression at line 85 … raise_exception('System message must be at the beginning')`；C `[user, system]`（首位不是 system）→ **同样 500**。取 `:8080/props` 的 chat_template（155 行）第 83-86 行确认：`{%- if message.role == "system" %}{%- if not loop.first %}{{- raise_exception(...) }}`。
- 结果：**PASS（根因确证）**
- 备注：jarvis 里唯一的第二条 system 来源是 `context.py:49`（窗口达 `summarize_after=8` 时把 `[Earlier context: …]` 作为 system 前缀）。设置页保存本身不写 context（`index.html:690-708` 只发 `llm.temperature/tts/stt/wake_word`；`web.py:141-163` 只 merge 这些键）——保存后用户继续多轮对话，窗口到 8 → 压缩 → 之后每个请求都 500；Ollama 未运行把真因掩盖成连接错误。
