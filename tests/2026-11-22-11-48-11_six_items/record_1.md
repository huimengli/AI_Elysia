# 轮 1 · 样式一致与滚动（第 1/4 条）

- **时间**：2026-11-22-12:26 → 12:28
- **场景**：真会话（jarvis 经 start_all_in_one.bat 起，7860/8080/9880 在听）；我的 tab 开「http://127.0.0.1:7860/monitor?v=4」，用 getComputedStyle(body) + scrollBy + 面板 head 文案 + 截图对照。
- **期望**：字体族照 home（PingFang SC / Microsoft YaHei）、背景含 radial-gradient、标题「监视界面 — 爱莉希雅」、overflowY=auto 且能上下滚动，日志面板各自可滚。
- **实际**：overflowY=auto ｜ 字体="PingFang SC", "Microsoft YaHei"… ｜ 渐变=true ｜ 标题=监视界面 — 爱莉希雅 ｜ scrollBy(0,300) 后 scrollTop=300（内容高 1275 > 视口 774）｜ 面板 max-height:220px/overflow:auto，pre.scrollTop 实测 18.4 ｜ head 文案「页面显示上限 200 行，全量写 .tmp/<name>.log」，第三面板显示名「爱莉希雅」。
- **结果**：**PASS**（第 1、4 条）。
- **备注**：照实记第 178 处自曝——我第一次量到的页是 Chrome 启发式缓存的旧版（overflowY=hidden、旧字体、旧标题），带 cache-buster 的 fetch 才是新版（9268 字符，标题/overflow/LOGCAP 全命中）。第 181/184 处坐实后三条页面路由加 Cache-Control: no-store。
