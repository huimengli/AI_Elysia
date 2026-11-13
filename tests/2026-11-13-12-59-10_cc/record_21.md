# 轮 21（附加项，不占 20 轮判据）— `delegate_task` 已按规矩摘除
- **时间**：2026-11-13 13:29
- **场景**：直调校验三处（TOOL_MAP / TOOL_SCHEMAS / TOOL_LABELS）并尝试 `dispatch('delegate_task', ...)`（零截图）
- **期望**（`records/2026-11-13-12-59-10.md` 新增规矩：**爱莉希雅不允许启动子智能体**）：模型侧完全看不到这条工具，调用被拒
- **实际**：
  ```
  TOOL_MAP 里有 delegate_task: False
  schema 里有 delegate_task: False
  中文标签里有: False
  工具总数: 32 32
  调用已被拒: 未知工具：delegate_task
  ```
- **结果**：**PASS**
- **备注**：`jarvis/tools/subagent.py` 文件保留未删（不动其它调用方）；`TOOL_MAP` 与 `TOOL_SCHEMAS` 数量一致（32），没有悬挂引用。
