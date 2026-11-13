# 轮 12 — `kill_process`（目标只用记事本，已授权）
- **时间**：2026-11-13 13:21 + 13:25（清场复用）
- **场景**：杀记事本后复查窗口列表；再喂一个不存在的进程名（零截图）
- **期望**：只杀指定进程；业务进程不动；杀不到要如实报
- **实际**：
  ```
  已结束进程：notepad
  记事本还在吗: False
  结束进程「zzz_not_exist」失败：ERROR: The process "zzz_not_exist.exe" not found.
  ```
- **结果**：**PASS**
- **备注**：`kill_process` 会把输入**清洗成字母数字/`.-_ `**再拼 `{name}.exe`（`jarvis/tools/app_control.py` 第 94 行），所以中文进程名会被洗成空串 → `taskkill /IM .exe`，行为不可预期。规矩：**进程名参数必须是英文进程名**，schema description 里该写清这一点。
