# 轮 9 — 说「把音量调大」（第 4 句指令）→ **工具虚假成功**

- **时间**：2026-11-13 12:12:48
- **场景**：唤醒后说「把音量调大」，之后你核对真实设备音量
- **期望**（脚本）：转录正字；音量真的被调大；回复与实际操作一致
- **实际**：
  ```
  12:12:48 wake  Wake word triggered
  12:12:56 user  把音量调大。
  12:13:03 assistant 音量已调至最大 (100%)。
  ```
  转录正字 PASS（整句完整）。**但设备音量实际仍是 20%（你核对）**。我绕开对话直接验工具本身（零截图，`python -X utf8` 直调）：
  ```
  before: 当前音量 0%。
  音量已设为 40%。      ← 工具声称成功
  after: 当前音量 0%。   ← 实际未变
  ```
- **结果**：**FAIL** —— 工具**虚假成功**：`set_volume` 跑完 PowerShell **不检查 returncode / 不检查输出**，无条件 `return f"音量已设为 {level}%。"`（[jarvis/tools/system.py](jarvis/tools/system.py:33)）。回复只是把工具字符串复述成「已调至最大 (100%)」，所以模型没撒谎，是**工具在撒谎**。顺带 `get_volume` 读的是 `GetDefaultAudioEndpoint(0,1)`（`eConsole` 端点），与你播放器上看到的 20% 不是同一端点，读数恒 0%。
- **备注**：已追加 `hard_bug.md` **HB-033**（虚假成功类）。这类比「编造回复」更危险：它让模型永远拿不到失败信号，2026-11-08 治理的「工具失败要直说」在这条上被工具本身架空。修法：`set_volume` 检查 returncode + 复读音量作为证据，失败时返回 `音量设置失败：<stderr>`；`get_volume` 改读 `GetDefaultAudioEndpoint(0,0)`（`eMultimedia`）。
