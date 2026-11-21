# 轮 8 · 搜索兜底（真机 bing 目标页落地能力）

- 时间：2026-11-21 11:15:06
- 场景：真机直开 bing 搜索页 `https://www.bing.com/search?q=爱莉希雅`（URL 编码），CDP 复读
- 期望：复读地址含 `bing.com/search`
- 实际：标题「**爱萅希雅 - 搜索**」，地址 `https://cn.bing.com/search?q=%E7%88%B1%E8%90%85%E5%B8%8C%E9%9B%85&rdr=1&rdrig=9EFCE71FC031`
- 结果：**PASS**
- 备注：www.bing.com 被重定向到 **cn.bing.com** 并带 `rdr` 参数；判据（含 `bing.com/search`）成立。标题里「萅」是页面渲染的字，不是我写的关键词 —— 照实记。本轮只验兜底页真能落地，不验反爬时机。
