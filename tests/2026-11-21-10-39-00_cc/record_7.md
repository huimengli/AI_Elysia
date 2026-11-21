# 轮 7 · 搜索兜底（真机 baidu 首选）

- 时间：2026-11-21 11:14:47
- 场景：真机 `search("爱莉希雅 官方")`（jarvis 自起窗口 + CDP 复读，profile `.tmp/chrome_profile`）
- 期望：首选 baidu 落到 `baidu.com/s?` 搜索页，返回含「已用 baidu」
- 实际：返回首句「搜索「爱莉希雅 官方」已用 baidu 打开浏览器：https://www.baidu.com/s?wd=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9」；起法「已用 chrome.exe 带参数启动…」；CDP 复读 标题「**爱莉希雅 官方_百度搜索**」 地址 `https://www.baidu.com/s?wd=%E7%88%B1%E8%90%85%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9`（无报错）
- 结果：**PASS**
- 备注：**本轮没有触发兜底** —— baidu 真机落到了搜索页。兜底的真机触发时机照旧未测。
