# 轮 3 · 2026-11-17 13:25:44 · HB-040 `_coerce` 修复验证

- **场景**：模型显式给 null（仍须防 NoneType 崩）
- **输入**：`{'seconds': 3600, 'message': None}`
- **期望**：期望 coerce 成空串（不崩）
- **_coerce 输出**：`{'seconds': 3600, 'message': ''}`（`message` 键在，值 ``）
- **实际（dispatch）**：已设置 1小时 0分 后的提醒：
- **结果**：PASS（显式 null 仍 coerce 成空串，工具不崩）
- **备注**：`seconds=3600` 只为让计时器在沙箱进程退出前不触发通知；旧实现会把省略的 `message` 写成 `""`（键存在于 dict），函数默认值被架空

