# 轮 9 · 搜索兜底（bing 兜底路径）

- 时间：2026-11-21 11:15:47
- 场景：代码路径打桩：baidu 落 wappass 反爬页（非真机反爬）
- 期望：兜底触发、URL 换成 bing、复读证据含 bing 地址
- 实际：搜索「爱莉希雅 官方」两个引擎都没有落到搜索页，**没有搜到**。
[打桩] 已按 jarvis 口径起窗口：https://www.baidu.com/s?wd=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9
页面证据：标题「百度安全验证」地址 https://wappass.baidu.com/passport/?logid=123
baidu 落不到搜索页（标题「百度安全验证」），换 bing 兜底
[打桩] 已按 jarvis 口径起窗口：https://www.bing.com/search?q=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9
页面证据：标题「爱莉希雅 - 搜索（打桩）」地址 https://cn.bing.com/search? || 调用序列 ["https://www.baidu.com/s?wd=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9", "https://www.bing.com/search?q=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9"]
- 结果：**PASS**
- 备注：打桩轮只验代码路径；真机反爬出现时机照旧未测（轮 7 真机 baidu 落到了搜索页）

打桩口径照实：本轮**不是真机反爬**，是把 `open_url` / `evaluate` 换成桩，验代码路径：baidu 落 wappass 验证页 → 返回里出现「换 bing 兜底」+ 调用序列第二条是 bing URL。

证据：`.tmp/logs/search_rounds.json`；驱动 `.tmp/search_test.py`（轮 7-8 真机部分）与 `.tmp/search_test2.py`（轮 9-11，stub 返回 (json, err) 二元组——第一版返回单串被 `s, e = evaluate(...)` 解包炸，第 61 处自曝）。
