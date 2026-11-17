# 轮 7 · 2026-11-17-11-42 · 三个数据源对照（同一把正则，量到三种结果）

- **场景**：同一个关键词「稻香」、同一个正则 `"bvid":"(BV[0-9A-Za-z]{5,})"`，在**三个不同来源**上量。
  共享浏览器（你能看到的窗口，真实登录会话）里用 `dsh_browser_execute` 跑正则，沙箱里跑 jarvis 原函数。
- **实际（逐字数据）**：

| 来源 | 字节 | 正则命中 | 第一条 | 说明 |
| --- | --- | --- | --- | --- |
| 浏览器渲染后的 DOM（`document.documentElement.outerHTML`，`search.bilibili.com/all?keyword=稻香`） | 1,048,951 | **0** | 无 | DOM 里有 **86** 条 `a[href*="/video/BV"]`，第一条 `https://www.bilibili.com/video/BV15es76gEgL`；HTML 含反爬字样（`captcha_word: true`） |
| jarvis urllib GET 同一 URL（轮 5） | **266,710** | **126** | `BV1Ki4y1y7HC` | **服务端 HTML 内嵌 JSON**，正则命中；与浏览器 DOM 不是同一份东西 |
| `api.bilibili.com/x/web-interface/search/all/v2?keyword=稻香`（浏览器内读 body 文本） | 31,355 | **20** | `BV1bRQBBDEKJ` | `code:0`，`video_count:20`，`json_first_bvid` 与正则第一条**一致**；harness 侧无 cookie 也拿到 `code:0` 20 条 |

- **结果**：**PASS（对照数据齐）**，结论三条：
  1. **Route A（服务端 HTML + 正则）在 jarvis 侧可用**（126 命中），**不需要改数据源**；我 11:36 的"必失败"判断是证据域搞错（DOM vs 服务端 HTML），已在轮 5 更正
  2. **"第一支视频"的口径有三种答案**：服务端 JSON 序（`BV1Ki4y1y7HC`，948 万播放的私藏馆版）、DOM 渲染序（`BV15es76gEgL`）、API 序（`BV1bRQBBDEKJ`，23 万播放的单曲循环版）。
     **要哪种由你定**（Q32）：你要的"第一支"= 列表第一张卡（肉眼看到的），还是 JSON 排序第一？
  3. **API 是最省字节的来源**（31 KB vs 266 KB），若改为 API 则字节与内存都更小；正则不用改（`"bvid":"…"` 在 API 里也命中）
