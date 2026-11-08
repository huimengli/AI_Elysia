# 轮 3：WS 事件驱动的渲染路径（2026-11-08-15:05）

- 场景：本机无浏览器（`playwright-online-search` 缺 chromium 可执行文件，`chromium install` 未成功；`web_fetch` 亦无网络），故用 node `vm` + 最小 DOM 桩（getElementById/createElement/appendChild/prepend/querySelectorAll/style/classList，`esc` 的 textContent→innerHTML 语义在桩中实现）加载页面 JS，按 `web.py` 的消息格式喂事件：`connected`、`user`、`tool`、`tool_result`、`response`、`mute`、`status(Thinking...)`。
- 期望：`onopen` 后状态为已上线并加载 provider；事件逐条落到聊天区/工具日志/实时流/状态条/反应堆标签，静音切换生效。
- 实际：`ws url: ws://127.0.0.1:7860/ws`；onopen 后 `statusText=已上线`、`reactorLabel=已上线`、`modelSelect` 载入 `Qwen3.5-2B`、历史 `历史记录测试` 入聊天区；`connected`→`爱莉希雅已上线。`；`user`→`语音输入 打开记事本` + 实时流；`tool`→`statusText=工具: FOCUS_WINDOW`、`activityText=执行: FOCUS_WINDOW`、activity 条 active、步骤点 2 个、工具日志 `focus_window`；`tool_result`→`activityText=处理结果`，工具日志条目追加 `ok`；`response`→`说话中` + 聊天区 `爱莉希雅已为你打开记事本`，activity 条收起；`mute`→`muteBtn.muted=true` + `🔇 已静音`；`status Thinking...`→`分析中` + `处理中`。断言 13 项全部命中，缺失 0。
- 结果：**PASS**（node 桩驱动，非真实浏览器渲染）
- 备注：**未做真实浏览器渲染验证**（无可用 chromium/Edge 可执行文件，且本机无外网）。需要用户在 `:7860` 启动 Jarvis 后浏览器目视验收（配色/动画/对比度）。桩局限：`querySelectorAll` 为单层实现，`.msg.tool-call`（嵌套层）未命中——该路径在真实 DOM 中有效；`esc()` 的转义结果与浏览器一致（& < >）。
