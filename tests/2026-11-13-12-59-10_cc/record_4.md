# 轮 4 — `open_url`（服务级，用本机 URL 避开外网）
- **时间**：2026-11-13 13:28:36
- **场景**：浏览器输入框打字「打开网址 http://127.0.0.1:7860/」（零截图）
- **期望**：打开成功、不报错；不要求抢前台
- **实际**（日志）：
  ```
  [Tool: open_url] 已在浏览器打开：http://127.0.0.1:7860/
  [TTS] queued: 1 segments, first sound 2804 ms, played 1.74 s, total 4382 ms
  ```
- **结果**：**PASS**
- **备注**：`open_url` 用 `webbrowser.open`（`jarvis/tools/app_control.py` 第 83 行），对非 `http(s)` 前缀自动补 `https://`；本机 URL 不需要外网，是验这条工具的正确靶子。
