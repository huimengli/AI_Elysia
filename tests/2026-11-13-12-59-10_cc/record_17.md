# 轮 17 — `set_timer`（3 秒）
- **时间**：2026-11-13 13:26
- **场景**：`dispatch("set_timer", {"seconds": 3})`，主线程等 4 秒（零截图）
- **期望**：到时弹出提醒，主线程不被阻塞
- **实际**：
  ```
  已设置 3秒 后的提醒：
  （主线程未被阻塞，等 4 秒让 toast 弹出）
  ```
- **结果**：**部分 PASS**：计时器本身不阻塞、文案正确；**提醒能否弹出取决于 `show_notification`**（修前必失败，修后走气泡）。同时暴露：`message` 缺省时 `_coerce` 给空串，文案尾巴是空的（「已设置 3秒 后的提醒：」）。
- **备注**：`set_timer` 的默认中文 `'定时到了！'` 写在 TOOL_MAP（`jarvis/tools/router.py`），而 schema 的 `required` 只含 `seconds` → 缺 `message` 时被 `_coerce` 覆盖成 `""`，**默认值被架空**。修法：`_coerce` 应该用 schema 的 `default` 或工具的默认值，而不是无脑给空串。这条写进 `hard_bug.md` HB-040 候选。
