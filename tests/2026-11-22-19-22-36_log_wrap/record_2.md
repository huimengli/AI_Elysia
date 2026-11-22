# 第 2 轮 · 喂超长连续串断行

- **时间**：2026-11-22 21:05–21:06
- **场景**：在同一真页里走页面自己的推送路径 `appendLogs`（与 `ws` 的 `logchunk` 同一条路），灌入两条无空格连续串：`https://example.com/very/long/path/` + `A`×1200 + `/tail/` + `B`×1200，以及 `JSON.stringify` 的 C×1500 + D×1500 + E×1500。
- **期望**：断行（不出现左右滚动）、无水平溢出、上下滚动仍可用、console 0。
- **实际**：
  - `maxLineLen = 4541`（单条逻辑行），`arrayLines = 200`（页面 200 行上限生效），`textLen = 15712`；两条串在页上完整存在（`containsUrl = true`、`containsJson = true`）。
  - `scrollW = 1329` == `clientW = 1329`，`scrollLeft = 0` → **无水平滚动**。
  - `scrollH = 4136`、`clientH = 220` → 视觉行 ≈238（`4136 / 17.4`）→ 连续串被 `word-break: break-word` 断行。
  - 上下滚动可用：`scrollTop = 0`（到顶）与 `scrollTop = 3916`（到底，`maxScroll = 3916`）都到达；过程中 `scrollLeft` 恒 0。
  - console 条目 **0**。
- **结果**：**PASS**
- **备注**：截图 `C:\Users\楼听\Downloads\r19_round2.png`。灌入用页面自身函数，不注入新逻辑。
