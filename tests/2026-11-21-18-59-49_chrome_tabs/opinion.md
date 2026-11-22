# 批次结论 · 2026-11-21-18-59-49_chrome_tabs（验证 3 轮，全 PASS）

- 「点击无法切换」的根因是**服务端没跑新代码**：7860 上 `fetch("/static/tabs.js")` 真状态码 404、顶栏不存在；7861（新代码）200 且 3 次点击 URL/高亮都跟着走。所以这条的解决办法是**重启 jarvis**，不是改顶栏代码。
- 证据口径：network 里的 `status 0` 是 resource-timing 行不暴露状态，不能当 404 用（第 131 处自曝）。要真状态码就用 `fetch`。
- 仿 Chrome 用「深色条 + 圆角凸起卡片 + 当前页亮底」三件事就够：`border-radius:11px 11px 0 0`、`height:30px`、`align-items:flex-end`、当前页粉渐变 + 深色字、其余暗紫 + hover 提亮。computed style 逐项读出，不靠肉眼。
- 标签文字全中文用字母表逐字判定（含英文=false），别用正则塞探针字符串（TS 解析器会炸，第 132 处）。
