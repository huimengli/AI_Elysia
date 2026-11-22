# 轮 20 · `_coerce` 剩余架空默认值全量审计（42 工具）

- 时间：2026-11-21 11:26
- 场景：逐工具逐 schema 属性直调 `_coerce`：①全省略 ②显式 `null` ③明显错类型值（`string` 给 12、`integer` 给 "abc"…）④函数中文默认是否保住 ⑤必填无默认清单
- 期望：HB-040 的洞（省略键被灌成 `""`/`0`/`False` 压掉函数中文默认）不再复发；把「剩余架空」清点干净
- 实际：42 工具 —— **省略键被注入 0 件**、**null 未强制 0 件**、**类型未强制 0 件**（HB-040 的修复在全量上成立）。「中文默认保护明细」= **空**，这条**是我的审计有洞**：`TOOL_MAP` 是 `lambda a: f(a["url"])`，`inspect.signature` 只看到一个参数 `a`，函数自己的中文默认在 lambda 里看不见（第 63 处自曝后记，不是代码里没中文默认）。
- 真洞（审计挖出来的）：**必填无默认 34 项**（`web_search.query`、`open_url.url`、`click_at.x/y`、`set_volume.level`、`set_timer.seconds`…）——模型省略必填键时 `a["url"]` 直接 **KeyError** → `dispatch` 吐「执行失败：…」灌回模型。**这正是 2026-11-08 关掉的幻觉通道从这条缝又漏了。**
- 结果：**PASS（审计目标达成，含挖出真洞）**
- 备注：驱动 `.tmp/coerce_audit.py`，明细 `.tmp/logs/coerce_audit.json`。修法见轮 21。