# 轮 2：baidu 真实搜索（2026-11-08-15:32）

- 场景：中文查询走 baidu 引擎（skill 的默认引擎）。
- 期望：exit 0 + 结构化结果。
- 实际：`node search.mjs "爱莉希雅 崩坏3 配色 粉色 白色 主题" --engine baidu --count 6` → **exit 0**，5 条结果：《崩坏3》官网、miHoYo 旗舰店爱莉希雅主题配饰、崩坏3WIKI「爱莉希雅」系列壁纸（圣芙蕾雅档案馆）等；链接为 baidu `link?url=` 跳转形式（引擎输出格式，非解析缺陷）。
- 结果：**PASS**
- 备注：无 captcha（未命中「百度安全验证」）。
