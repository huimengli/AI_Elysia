# 轮 1 — HB-033：`set_volume` 复读音量作为证据 + COM 激活 + TEMP 重定向

- **时间**：2026-11-13 12:25-12:29
- **场景**：修完后重启 `:7860`，在浏览器输入框打字「把音量调到60」→「把音量调回20」（零截图），并用独立 python 复测音量
- **期望**（`hard_bug.md` HB-033 方案）：只有**复读音量与目标一致**才报成功；读不到/不符必须报失败；音量读的是播放器所在端点（`eMultimedia`）
- **实际**：
  - **根因 1（虚假成功）**：老实现不检查 returncode/输出，无条件返回成功 → 12:13:03 回复「已调至最大 (100%)」而设备 20%。
  - **根因 2（COM 激活）**：`[MMDeviceEnumerator] -as [IMMDeviceEnumerator]` 在 PowerShell 里**返回 null**，整条链打在 null 上（`probe .tmp/vol_probe.ps1` → `role=1 rc= no device`、`role=0 rc= no device`）。改成 C# 类里 `new MMDeviceEnumerator()` 做 COM 激活后（`.tmp/vol_probe2.ps1`）：
    ```
    LanguageMode: FullLanguage
    multimedia(0) now: 20
    console(1)   now: 20
    after set 40 role0 -> readback: 40
    after set 20 role0 -> readback: 20
    ```
  - **根因 3（沙箱禁写 Temp）**：服务作为 harness 后台任务启动时，python 子进程的 `%TEMP%` 禁写 → `Add-Type` 编译被拒（12:25:43 那次回复「系统权限不足无法修改音量设置」，日志 26 行 `Access to the path '...\Temp\1wrwgndj.tmp' is denied`）。把 `$env:TEMP` 指到工作区 `.tmp/pscompile` 后（`training/_t3_temp_probe.py`）：**rc 0、`[AudioVol]::Get(0)` → 20、无 ERR**。
  - **修后直调（工具级）**：
    ```
    before: 当前音量 20%。
    音量已设为 60%（已复读确认）。
    after: 当前音量 60%。
    音量已设为 20%（已复读确认）。
    restored: 当前音量 20%。
    ```
  - **修后服务级（浏览器打字）**：日志 26 行 `[Tool: set_volume] 音量已设为 60%（已复读确认）。` → 独立复测 `当前音量 60%。`；日志 36 行 `[Tool: set_volume] 音量已设为 20%（已复读确认）。` → 独立复测 `当前音量 20%。`
- **结果**：**PASS**。三层根因全部封住，且「虚假成功」变成「复读证据 + 如实报失败」。
- **备注**：浏览器 console 在这期间有 20 条 error，**全部是重启窗口里的 `ERR_CONNECTION_REFUSED`**（`/api/health`、`/api/events`、`ws://…/ws`），没有新错误类别；4 灯重启后全 online（`v0.9 / 0.75`）。
