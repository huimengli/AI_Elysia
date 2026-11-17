<!-- 已归档于 ai_buckup/hard_bug.md_2026-11-17-13-26-51.md（全量备份，含 HB-047 立案结案、11-06 更正、HB-040 结案）；本文件只保留结案摘要 -->

# hard_bug（compact，已解决）

- **影响**：模型省略可选参数时，播报/行为用**空串**而不是函数的中文默认值（`set_timer` 定时提醒不播报文案）
- **现象**：`dispatch('set_timer', {'seconds':3600})` → 「已设置 1小时 0分 后的提醒：**（空）**」
- **尝试**：只读 `_coerce` 与 schema，确认 schema 里 `message` **没有** `default` 字段，函数默认值是唯一来源
- **根因**：`jarvis/tools/router.py::_coerce` 遍历**所有** schema 属性写值，`out.get(key)` 缺席时得 `None`
  → 被写成 `""`，且**键存在于 dict** → `set_timer(seconds, message="定时到了！")` 收到 `""`，默认值被架空
- **方案**：`if key not in out: continue`（模型没传就不注入，函数默认值生效）；显式 `null` 仍 coerce（防 `NoneType` 崩）。
  **不改 schema 文案、不增删工具**（工具面 token 不变）
- **验证**：**3 轮全 PASS**（`tests/2026-11-17-13-25-00_coerce/record_1..3.md` + `opinion.md`），附加 `click_at` 缺省 `button` 生效
- **关联**：`records/2026-11-17-13-25-00.md`、`records/2026-11-13-*`（立案）、`events.db` 242/245（当年崩溃源）
- **归档**：本条结案后 `hard_bug.md`（HB-047 立案结案 + 11-06 更正 + 本条）全量备份到
  `ai_buckup/hard_bug.md_2026-11-17-{ts_tail}.md`，原文件 compact + 顶部归档注记（§3）

