# 轮 3 · 2026-11-21-18-37-00 · 点 about 标签 + 回切主界面

时间: 2026-11-21 18:37
场景: 在 monitor 页点「about（相关页面）」，再点「主界面」回切
期望: `/about` 出现且只写已实现的事实、高亮跟着走、回切后 URL 与页面一致、console 无 error
实际: `URL=/about ｜ 高亮=about（相关页面） ｜ 标题=about — 项目现状（不写没实现过的功能） ｜ 表 5行,6行,8行 ｜ 未测条数=3 ｜ tokens/s条=true ｜ console(含error) 0` → 截图 [C:\Users\楼听\Downloads\tabs_about.png](C:\Users\楼听\Downloads\tabs_about.png)；回切 `URL=/ ｜ 高亮=主界面 ｜ 标题=爱莉希雅 ｜ 顶栏存在=true`。
结果: **PASS 4/4**（about 内容：组件端口表、模型与阈值 0.75 不可改、埋点口径含 `tokens/s` **未埋**、缓存 TTL 、未测项 3 条）
备注: `about` 是新页 + 新路由 `@app.get("/about")`；静态资源靠新加的 `app.mount("/static", StaticFiles(...))` 出 `tabs.css`/`tabs.js`。
