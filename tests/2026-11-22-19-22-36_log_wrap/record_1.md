# 第 1 轮 · 自然长行无水平滚动

- **时间**：2026-11-22 21:03–21:05（本地 Asia/Shanghai）
- **场景**：真浏览器打开 `http://127.0.0.1:7860/monitor?ts=<cache-buster>`；jarvis 真在跑（`.tmp/jarvis.log` 每 ~3 s 一行，21:01 起持续写入），三面板自然灌入 llama / tts / 爱莉希雅日志。
- **期望**：`scrollWidth <= clientWidth`（无水平溢出）、`scrollLeft` 恒 0、长行换行可见、console 0、真页截图。
- **实际**（真页 `getBoundingClientRect` / `getComputedStyle` 量出，不推断）：
  - 面板数 3；三面板 `clientW = 1329`、`scrollW = 1329`、`scrollLeft = 0`。
  - `overflowX: hidden`、`wordBreak: break-word`、`whiteSpace: pre-wrap`、`lineHeight = 17.4 px`。
  - 最长行：llama 153 字符、tts **3769** 字符、爱莉希雅 43 字符；tts 面板 73 条 → 视觉行 ≈108（`scrollH 1891 / 17.4`）→ 换行真发生。
  - 垂直滚动条宽 `offsetWidth - clientWidth = 8 px`（照 home 口径）。
  - console 条目 **0**；`dsh_browser_network(onlyFailures)` 只列出 resource-timing 的 status 0（该通道不暴露状态），无真实失败。
- **结果**：**PASS**
- **备注**：本轮开工前先修好一处把页面整块 JS 弄坏的改动（自曝 250）；修后 `new Function(<script>)` parse OK。截图 `C:\Users\楼听\Downloads\r19_round1.png`。
