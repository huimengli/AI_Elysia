# 批次结论（tests/2026-11-08-17-53-00_cc，验证 3 轮）

- 根因：**不是设置页保存本身**，而是保存后继续多轮对话使 `context` 窗口达到 `summarize_after=8` → `context.py:49` 把 `[Earlier context: …]` 作为第二条 system 消息 → Qwen3.5 chat template 第 85 行 `raise_exception('System message must be at the beginning')` → 8080 返回 500；jarvis 回落 Ollama（未运行）→ 用户看到「连接不上 Ollama」，真因被掩盖。三组探针（A 正常 / B 第二条 system 500 / C 首位非 system 500）确证。
- 修复（commit fix(AI)）：`main.py::_process_request` 把前导 system 摘要并入唯一 system 消息，并让主 provider 失败时在 `status` 事件与事件库写出**主错误**；`jarvis/llm.py` 的 openai 分支补 `chat_template_kwargs.enable_thinking`（否则 content 全空）并把 `timeout` 15→90（子代理/摘要此前被 15 s 掐断后回落 Ollama）。
- 3 轮验证：轮1 根因确证；轮2 连续 5 轮对话（窗口达 8 触发压缩）5 条 response 全出、无 500；轮3 重启后 UI 200/42,420 B、API 200、TTS 200/266 KB RIFF、WS 对话正常。
- 运维提醒：重启 jarvis 必须 `Stop-Process` 掉旧的 python（job kill 只杀 pwsh 外层，`job_kill` 后旧实例仍占 :7860，导致新实例 `10048 端口已占用` 退出）。
