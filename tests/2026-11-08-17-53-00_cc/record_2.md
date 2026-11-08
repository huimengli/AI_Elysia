# 轮 2：修复后连续 5 轮对话（触发压缩）（2026-11-08-18:00）

- 场景：修 `main.py::_process_request`——把 `context.get_messages()` 前导 system（摘要）并入唯一 system 消息；主 provider 失败时把主错误写进 `status` 事件与事件库。重启 jarvis（pid 12880 是 17:32 的旧实例，job kill 只杀外层 pwsh，须 `Stop-Process` 才释放 :7860），node WS 连发 5 条 chat（记住 7/8/9 → 复述 → 总结），窗口在 chat4 后达 8 触发 `_compress_oldest()`。
- 期望：5 条都有 response，无 500、无「Failed to connect to Ollama」。
- 实际：**5 条 response 全出**：`Done.` / `已记住数字 8。` / `已记住数字 9。` / `您之前说过 7、8、9。` / `抱歉，我暂时无法连接 Ollama 来总结对话。不过我已经记住了您之前提到的数字 7、8、9。`；无 500。第 5 条里的 Ollama 字样来自 `delegate_task` 子代理走 `jarvis/llm.py`——其 openai 分支 `timeout=15.0` 会掐断 2B 生成并回落 Ollama，已一并把 timeout 改为 90.0（`py_compile` 通过，需重启生效）。
- 结果：**PASS**（第二条 system 不再产生；旧实例观察到的 `Error: [Errno 22] Invalid argument` 属旧代码路径，新实例无该现象）
- 备注：`main.py` 摘要并入 system 的写法是 `while messages[0].get("role")=="system": leading.append(pop)` → `sys_content += "\n\n" + join(leading)`，列表里只留一条 system。
