# 轮 2 · 2026-11-16-12-48-23

- **时间**：12:46 重启 7860（`pwsh-35`，日志 `.tmp\bats\start7860_1246.log`），12:47:23 复核 4 灯，12:48:23 点击，12:48:59 读数
- **场景**：第 2 条复测。共用浏览器（tab `ca779fdc…`，**零截图**）JS 点「播放音乐」（`data-cmd` = `用浏览器打开B站搜索《稻香》并播放第一支视频`）
- **期望**：`open_url` 被调用，URL = `https://search.bilibili.com/all?keyword=稻香`；进入视频页，`<video>` 时长非 0、`paused=false`
- **实际**（jarvis 日志 + `/api/events`，两口径一致）：
  1. `[Tool: web_search] 搜索失败：ConnectError: ConnectError('error sending request for url (https://search.yahoo.com/search;_ylt=…` —— **我这一侧沙箱里 python 子进程无网络**（文档化边界），联网搜索在我这儿必然失败；这不是我改代码造成的，也不代表你直接跑 jarvis 时的表现。
  2. `[Tool: open_app] 已打开：Google Chrome（从应用列表匹配，复读确认进程 chrome）` —— 应用表命中 ✓，复读确认 ✓
  3. `[Tool: type_text] 已输入文本（剪贴板粘贴，2 个字符键盘打不出）：稻香` —— 中文走剪贴板粘贴的修复真生效 ✓
  4. **`open_url` 没有被调用**（日志 `[Tool: open_url]` 零条），没打开 B 站搜索页；12:48:59 助手回复 `我执行了 联网搜索、打开应用、输入文本：已输入文本（剪贴板粘贴，2 个字符键盘打不出）：稻香`
  5. 事件账本这次**有** assistant 事件（上一轮没有）—— `web.py` 的落盘改动起作用
  6. 4 灯：12:47:23 `wake=True asr=True llm=True tts=True`，`model=aili_xiya_v0.9.onnx thr=0.75`；可用提交 1,108 MB，本轮**没有** ONNX `bad allocation`
  7. 日志另有 `WebSocketDisconnected: WebSocket is not connected. Need to call "accept" first.` traceback（`ws.accept()` 在 L339 存在）—— 记为观察，未下结论
  8. `TTS] queued: 4 segments, first sound 3772 ms, played 12.10 s, total 21962 ms`
- **结果**：**未达标**。中文命令 ✓、应用表 ✓、剪贴板粘贴 ✓、事件账本可见 ✓；`open_url` **0 次被选中** → B 站播放未达成。
- **备注**：副作用 —— **真的打开了 Chrome**（未关），在 Chrome 焦点粘贴了 `稻香`（先存后还）；未产生文件。零截图。
