# 轮 10 · 搜索兜底（bing 兜底路径）

- 时间：2026-11-21 11:15:47
- 场景：代码路径打桩：两引擎都落不到搜索页
- 期望：如实报没有搜到，不谎称搜到
- 实际：搜索「爱莉希雅 官方」两个引擎都没有落到搜索页，**没有搜到**。
[打桩] 已按 jarvis 口径起窗口：https://www.baidu.com/s?wd=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9
页面证据：标题「打桩：两引擎都没落地」地址 https://example.com/none
baidu 落不到搜索页（标题「打桩：两引擎都没落地」），换 bing 兜底
[打桩] 已按 jarvis 口径起窗口：https://www.bing.com/search?q=%E7%88%B1%E8%8E%89%E5%B8%8C%E9%9B%85%20%E5%AE%98%E6%96%B9
页面证据：标题「打桩：两引擎都没落地」地址 https://example.com/none
baidu 落不到搜索页（标题「打桩
- 结果：**PASS**
- 备注：判据是 CDP 地址，不是外观；hallucination 通道照旧关着


证据：`.tmp/logs/search_rounds.json`；驱动 `.tmp/search_test.py`（轮 7-8 真机部分）与 `.tmp/search_test2.py`（轮 9-11，stub 返回 (json, err) 二元组——第一版返回单串被 `s, e = evaluate(...)` 解包炸，第 61 处自曝）。
