# 轮 3：duckduckgo 引擎（2026-11-08-15:34）

- 场景：`--engine duckduckgo --timeout 45000`（默认 20000 首试超时后加长）。
- 期望：exit 0 + 结果；若引擎不可达则如实记录。
- 实际：**exit 5**，`page load failure: net::ERR_CONNECTION_TIMED_OUT at https://html.duckduckgo.com/html/?q=...`，results=0。补充轮（同引擎换查询 `爱莉希雅 刻印 饰品 逐火十三英桀 位次`，bing）→ **exit 0** 6 条结果（引擎质量参差，首条命中爱奇艺/「爱」字百科，说明抓取与解析链路正常，相关性由搜索引擎排序决定）。
- 结果：**PASS（skill 侧）**，duckduckgo 引擎在本机网络不可达（exit 5 是 skill 的正确上报，不是崩溃）
- 备注：本机 bing/baidu 可达，duckduckgo 连接超时；后续搜索请默认用 bing/baidu。
