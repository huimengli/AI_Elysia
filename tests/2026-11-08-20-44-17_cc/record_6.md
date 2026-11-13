# 轮 6 — 说「爱莉希雅，打开记事本」（第 1 句指令）

- **时间**：2026-11-13 12:10:31
- **场景**：唤醒后立刻说指令「打开记事本」，说完停 3 s
- **期望**（脚本）：转录正字（可辨认原句，相似度 ≥0.8）；无「话没说完被截断」；LLM 有回复且 TTS 出声；工具失败要直说
- **实际**：
  ```
  12:10:31 wake  Wake word triggered
  12:10:43 user  爱莉希雅
  12:11:03 assistant 我执行了 发送通知、发送通知、发送通知：工具「发送通知」执行失败：'NoneType' object has no attribute 'strip'
  ```
  **指令整句丢失** —— 转录只有唤醒词本身（`爱莉希雅`），「打开记事本」四个字没进转录；模型把这段当指令，连调 3 次 `show_notification`（空参数 → `title=None` 之类），每次都以 `'NoneType' object has no attribute 'strip'` 失败。
- **结果**：**FAIL**（转录正字判据不满足：指令 0/4 字）。附带正面一面：工具失败被**如实说进回复**（系统提示「工具失败要直说」在 2026-11-08 治理里落地并生效），没有编造「已打开记事本」。
- **备注**：`'NoneType' object has no attribute 'strip'` 正是 `records/2026-11-08-20-44-17.md` 前置只读事实里记的现象（242/245 行同一句），**当时计划的「dispatch 按 schema 强制参数类型」没有落地** —— [jarvis/tools/router.py](jarvis/tools/router.py:58) 仍是 `show_notification(a["title"], a["message"])` 直传，[jarvis/tools/system.py](jarvis/tools/system.py:141) 的 `title.replace(...)` 在 `title=None` 时会炸。指令丢失与「唤醒后录音窗口起点」相关，见轮 7 对照。
