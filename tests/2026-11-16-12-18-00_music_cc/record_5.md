# 轮 5 · 2026-11-17-11-38 · `first_bilibili_video` 在沙箱实跑（丙方案 Route A 的数据侧）

- **场景**：沙箱内直接调用 jarvis 现代码，不经过模型：
  `.venv\Scripts\python.exe -c "from jarvis.tools.app_control import first_bilibili_video; print(first_bilibili_video('稻香'))"`
- **期望**（我此前写进 `records/2026-11-17-11-01-00.md` 的判断）：沙箱 python 子进程**无外网**，
  `first_bilibili_video` 拉 B 站会失败
- **实际**（工具原话，逐字）：
  `第一支视频：https://www.bilibili.com/video/BV1Ki4y1y7HC（搜索页 266710 字节，共 126 个 bvid）`
- **结果**：**PASS（数据侧通）**，并且**推翻我自己的两条前置判断**：
  1. **沙箱 python 子进程有外网** —— 之前"无外网"的依据只有 `web_search` 的 `ConnectError`，这条工具实测是
     266,710 字节的真页面，所以"无外网"结论**不能推广**，已作废
  2. **"jarvis urllib 只会拿到验证码页"不成立** —— 服务端 HTML 里带 JSON，`"bvid":"(BV[0-9A-Za-z]{5,})"`
     命中 **126** 次；我 11:36 在共享浏览器里量到的 **0 命中**是**渲染后的 DOM**（`outerHTML`），
     两者不是同一个东西，我在记录里把 0 命中当作"Route A 必失败"是**错的**（轮 7 有对照数据）
- **备注**：第一条 `BV1Ki4y1y7HC` = API 里 `rank_index:1` 的「【私藏馆】周杰伦《稻香》超治愈神作」（948 万播放），
  **不是**搜索页 DOM 的第一张卡（DOM 第一是 `BV15es76gEgL`）→ "第一支视频"的口径由数据源决定，需在 Q32 里定口径
