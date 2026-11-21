# 轮 1 · 2026-11-21-19-02-00 · 第 1 条根因诊断 + 全中文与仿 Chrome 外观

时间: 2026-11-21 19:00-19:02（沙箱 `uvicorn jarvis.web:app --port 7861`，不占你的 7860）
场景: 真浏览器分别开你的 7860 与沙箱 7861，读顶栏是否存在与资源真状态码
期望: 坐实「点击无法切换」的根因（不猜），并验标签全中文、外观仿 Chrome
实际: 7860 → `顶栏不存在（body 第1子节点 class=undefined）`，`fetch("/static/tabs.js")` 真状态码 **404**；7861 → `fetch("/static/tabs.js")` 真状态码 **200**（`content-type: application/javascript`）+ 顶栏在。7861 外观实测：条 `高36px 底 rgb(21,15,31)`；三标签 `主界面[高亮] / 监视界面 / 相关页面`，`圆角 11px`、`高 30px`，非当前页底 `rgb(36,26,49)`，当前页是粉→粉深渐变（`backgroundColor` 为 transparent，因为用渐变），每标签前有 8 px 圆点（粉/丁香/金）。截图 [C:\Users\楼听\Downloads\chrome_tabs_index.png](C:\Users\楼听\Downloads\chrome_tabs_index.png)
结果: **PASS**。第 1 条根因照实：**你的 jarvis 跑旧代码（无 `app.mount("/static", …)`），顶栏根本没被加载 → 点不动，不是顶栏代码坏**（沙箱新代码 3 轮点击都真切换）。
备注: **第 131 处自曝**：我先前拿 network 里的 `status 0` 当 404 证据——不成立（status 0 是 resource-timing 行不暴露状态，`/api/health`、`/api/events` 也全是 0 却成功）。改用 `fetch` 取真状态码才算证据。
