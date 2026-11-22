# 第 3 轮 · 上滚看历史不被覆盖 + 回底部恢复追加（含 HB-055 复验）

- **时间**：2026-11-22 21:06–21:08
- **场景**：真页挂 `ws.onmessage` 计数（包一层再交给原 handler），先向上滚到顶进入「查看」态，挂 9 s 收推送；再切回「最新追加」态挂 12–15 s。
- **期望**：上滚查看历史时视野不被新推送顶走；回底部后恢复追加、新行落底部；滚动条照 home 口径（8 px、粉→玫红）。
- **实际**：
  - 滚到顶后 `scrollTop = 0`、`follow = false`、模式按钮文字「查看」、状态文字「查看（视野冻结，向上滚看历史，最多 200 行）」。
  - 9 s 内 `logchunk` 到达 **3** 条，`scrollTop` 仍 0、`textLen` 仍 15712（尾行停在 `21:06:28`）→ **查看态冻结成立，未被覆盖**。
  - 点「最新追加」后回到追加态：12 s 收到 4 条、15 s 收到 4 条，尾行从 `21:07:35` 推进到 `21:07:47`，`scrollTop = 3916` == `maxScroll`（停在底部）。
  - **HB-055 复验（真测）**：追平后的老客户端持续收到增量（`logchunk` 3+4+4 条 / 9+12+15 s），页上尾行随真实时间推进 → `logs_since` 按单调序号取增量这条修法坐实。挂计数前的旧行为是 6 s 到达 0（`hard_bug.md` HB-055 现象行）。
  - 滚动条 `offsetWidth - clientWidth = 8 px`（三面板同值）；`::-webkit-scrollbar` 在页内声明 width 8 px + `linear-gradient(var(--pink), var(--rose))` + 圆角 8 px + track 透明。
  - console 条目 **0**。
- **结果**：**PASS**
- **备注**：截图 `C:\Users\楼听\Downloads\r19_round3.png`、`r19_round3b.png`。程序化设 `scrollTop` 后 `onscroll` 不在同一 tick 触发（同 tick 读到 `follow` 未变是事件时序，不是缺陷）；改点按钮后复验，追加态正常。
