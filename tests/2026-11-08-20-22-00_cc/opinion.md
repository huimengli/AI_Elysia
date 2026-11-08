# 批次结论（tests/2026-11-08-20-22-00_cc，验证 3 轮）

- 「网页端要刷新才显示」不是广播坏了：真实页面 2 s 内就能看到 `user/tool/tool_result/response` 气泡。真正的 bug 是前端 `case 'status'` 只匹配英文字面量（`Thinking...`/`Listening...`…），后端发的是中文（`思考中…`/`正在聆听…`/`在。`/`已停止。`/`主模型失败：…`）→ 状态灯、活动条、状态文字一直停在 `待命`，观感就是「页面不动，刷新才有新内容」。修法是同时匹配中文+英文，并在 `onopen` 加 20 s 心跳 + 每次（重）连重拉历史，`onclose` 清理心跳。
- 断线恢复实测：主动 `ws.close()` → `离线` → 3 s 后自动 `已上线`（重连 + `loadHistory()`），不需要刷新。
- 测试手法可复用：Playwright `channel: msedge` + `addInitScript` 包裹 `window.WebSocket` 记录消息时序（reload 会清页面注入）；改 `index.html` 不需重启 jarvis（FastAPI 从磁盘读）。当前 jarvis = **job pwsh-50**；llama `:8080`、GPT-SoVITS `:9880`（pwsh-10，pid 4436）未重启。真人测试会往事件库写 user/assistant 行。
