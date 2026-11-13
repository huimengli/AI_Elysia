# 轮 19 — `power_command` 拒绝分支 + `screenshot`（**HB-039 桌面禁写**）
- **时间**：2026-11-13 13:26
- **场景**：喂未知 action `reboot`（**不真执行任何电源操作**，按授权只测拒绝分支）；`screenshot('jarvis_tool_test.png')` 只验产物文件与字节，不读图
- **期望**：未知 action 返回提示文案、不执行；screenshot 产物落在可写位置并报告真实路径
- **实际**：
  ```
  未知 action: 未知电源操作：reboot，请用 shutdown/restart/sleep。
  修前 screenshot：PermissionError: [Errno 13] Permission denied:
      'C:\Users\楼听\Desktop\jarvis_tool_test.png'
  修后 screenshot: 截图已保存：C:\Users\楼听\Desktop\git\JarvisAi\.tmp\screens\tooltest.png（419024 字节）
  ```
- **结果**：**拒绝分支 PASS；screenshot 修后 PASS**
- **备注**：`power_command('reboot')` 走的是拒绝分支（只认 `shutdown/restart/sleep`），**没有触发任何关机/重启**。screenshot 写 `~/Desktop` 在 harness 后台任务里禁写（HB-033 延伸同一族），改到工作区 `.tmp/screens`。**截图产物只在本机，不进我的会话** —— 「零截图」是 Agent 会话侧的约束，爱莉希雅本地截图无问题。
