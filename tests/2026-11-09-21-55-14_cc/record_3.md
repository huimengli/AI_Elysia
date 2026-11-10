# 第 3 轮 · 工具播报汉化（type_text → 输入文本）

- 时间：2026-11-10 16:47–16:50
- 场景：
  1. 在 `jarvis/tools/router.py` 加 `TOOL_LABELS`（33 个工具的中文显示名）+ `tool_label()`；`main.py` 的 `_tool_report()` 与 `tool`/`tool_result` 广播（llamacpp 与 ollama 两条分支共 4 处）都带上中文；`index.html` 用 `msg.label || msg.name` 显示状态条/活动条/工具日志/实时流。
  2. 直接调用 `_tool_report` 断言文案；再用 WebSocket 真发一条聊天（`{"type":"chat","text":"现在几点了？用一句简体中文回答"}`）到 `ws://127.0.0.1:7860/ws`，抓广播事件里的 `label` 字段。
- 期望：TTS/网页文案为「我执行了 输入文本、按下按钮」，事件里英文 `name` 保留可检索，新增 `label` 为中文
- 实际 ①（`.tmp\bats\tool1.log`）：

```
labels=33 tools=33 missing=[]
report=我执行了 输入文本、按下按钮：OK enter
report_time=我执行了 看时间：21:59:00 星期二
label_type_text=输入文本 label_press_key=按下按钮
label_unknown=foo_bar
```

- 实际 ②（真人经网页端触发，`.tmp\bats\ws1.log`，16:49:28）：

```
tool_events=[["tool", "get_time", "看时间"], ["tool_result", "get_time", "看时间"]]
final=现在是 2026年11月10日 16点49分，星期二。
```

- 结果：**PASS** — 33 个工具全部有中文名（无遗漏），文案与用户给的示范完全一致（`type_text → 输入文本`、`press_key → 按下按钮`）；广播事件同时带 `name`（英文，检索用）与 `label`（中文，播报/UI 用）；未知工具名回退为原名，不会崩
- 备注：本轮顺带记录一个**与需求无关的既有问题**（不改代码，仅登记）：真实唤醒那次 30 s 录音到上限后转写两次都 `ConnectError WinError 10054`（`.tmp\jarvis3.log:13-23`，`asr.warm=false`、`device: cuda`），且 VAD 在环境噪声下会录满 30 s；这是 STT/VAD 侧的老问题，建议后续单独开需求处理。
