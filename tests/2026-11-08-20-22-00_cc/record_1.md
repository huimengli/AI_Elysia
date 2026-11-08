# 轮 1：修复前基线 — 后端广播是好的（2026-11-08-20:24）

- 场景：headless Edge（Playwright + `channel: msedge`，`PLAYWRIGHT_BROWSERS_PATH=F:\playwright-browsers`）打开 `http://127.0.0.1:7860/`，包裹 `window.WebSocket` 记录消息，发送一条聊天后每 2 s 数气泡。
- 期望：判定「不实时」是后端没广播，还是前端没渲染。
- 实际：气泡 140 → 143（t=0）→ 147（t=2 s）；WS 序列 `connected:爱莉希雅已上线。` → `user:测试实时刷新：请回答收到` → `status:思考中…` → `tool:get_time` → `tool_result:get_time` → `response:当前时间显示为 2026-11-08 20:22:59，星期日。收到。`。状态文字始终 `待命`（`case 'status'` 只匹配英文）。
- 结果：**PASS（定位到前端状态字符串不匹配，广播正常）**
- 备注：坑 —— `window.WebSocket` 包裹必须在 `addInitScript`（reload 会清空页面注入）；Playwright 在 Windows 用 `import 'file:///C:/...'` 绝对路径；`msedge` 需要真实 `PATH`/`LOCALAPPDATA`（`process.env` 为空，用 pwsh 采 19 个变量后传入）。
