# 第 2 轮 · about 页样式照 home 改（真窗口截图 + computed 样式 + console）

- **时间**：2026-11-22-14:52 → 14:56（jarvis 未重启，静态页每次请求现读）
- **场景**：真浏览器先后开 `http://127.0.0.1:7860/?v=51`（home，真文件是 `index.html`）与 `http://127.0.0.1:7860/about?v=61`，逐条量 computed 样式，再截真窗口图。
- **期望**：about 风格照 home（同一套 CSS 变量、同一多层渐变背景、同一字体、表格/段落成玻璃卡）。
- **实际照实**：第一次量 about 全部落空（table/p/ul 圆角 0、阴影 none、backdrop-filter none、`body::before` 背景 none/高 auto、body 只有 1 层 linear-gradient）→ 照实查磁盘与页内真 `<style>`（页里 539 字符、radial-gradient/backdrop-filter/body::before 全 false，与磁盘一致，不是缓存骗）→ 照实照出我的重写块被追加在 **`</html>` 之后**（58–90 行游离在文档外，浏览器不认），照实记为**第 220 处自曝（第 176 处同类续犯：报告了未生效的内容）**。照实把重写块搬进 `<head>` 的 `<style>`（行 9–43，`:root` 1、`body::before` 1、radial-gradient 3、backdrop-filter 2，`</html>` 是末行 84）后复量：table/p/ul `border-radius 16px` + `box-shadow rgba(20,10,30,0.45) 0 10px 34px` + `backdrop-filter blur(10px)`；`body::before` 2 px 粉条（linear-gradient 90deg）；body 背景 4 层渐变（3 radial + 1 linear）；字体 `PingFang SC, Microsoft YaHei`；h1 粉 `rgb(248,169,196)`、h2 粉白 `rgb(255,216,232)`、code 金 `rgb(242,201,168)`；真窗口截图照出顶部粉条 + 紫粉多层渐变 + 卡片式表格（圆角+阴影+玻璃）+ 顶栏三页（主界面/监视界面/相关页面）+ 右缘滚动条（红底 + 蓝紫圆角 thumb）。console 0 条。
- **结果**：**PASS**（第 4 条）。
- **备注照实**：第 221 处自曝——我用 pwsh 读 `home.html` 得 0 行，照实查目录才知 home 真文件是 `index.html`（55 KB，`<style>` 17,375 字符），照实照抄它的 `:root`、`body::before` 与卡片规则（`border-radius:16px` + `box-shadow:var(--shadow)` + `backdrop-filter`），不发明命名。照实把「当前 v3.2」改成「当前 v3.5」（design.md 现版本）。
