# 轮 16 — `show_notification`（**HB-037：整条 UWP toast 路径不可用**）
- **时间**：2026-11-13 13:26 首测（修前）/ 13:30 修后 / 13:31:22 服务级
- **场景**：直调 + `dispatch` 传空字典（走 `_coerce`）+ 浏览器打字「弹一个通知，标题是「爱莉希雅」，内容是「服务级验收」」（零截图）
- **期望**：通知真弹出来；参数缺失不崩
- **实际（修前）**：正常参数与空参**都失败**，stderr 三段：
  ```
  Collection was modified; enumeration operation may not execute   ← 模板 1 的 text 节点枚举
  You cannot call a method on a null-valued expression            ← $text[1] 为 null
  Exception calling "CreateToastNotifier": "The process has no package identity.
      (Exception from HRESULT: 0x80073D54)"                        ← 根因
  ```
  根因：**UWP toast 必须由有包标识的应用创建**，Python/PowerShell 进程没有包标识 → 这条路径在这台机器上**永远弹不出来**；老实现把全崩的路径包装成「已弹出通知：{title}」（虚假成功）。
- **修后（NotifyIcon 气泡，不需要包标识）**：
  ```
  轮1 正常参数: 已弹出通知：爱莉希雅 — 三条修复验收
  轮1 空参:     已弹出通知： —
  服务级 13:31:32 assistant: 已成功弹出标题为「爱莉希雅」，内容为「服务级验收」的通知。
  ```
- **结果**：**修后 PASS（工具级 + 服务级）**。诚实边界：**气泡是否真在你屏幕上出现，我无法验证**（PS 只回 `balloon shown`，没有可读的呈现证据），需要你肉眼确认。空参走 `_coerce` 得到空串，文案是「已弹出通知： —」，**不崩**。
- **备注**：20 轮轮 6（12:11:03）当时看到的 `'NoneType' ... 'strip'` 是 `text=True` 的 GBK reader 线程崩（`result.stderr` 变 None）——**不是缺参数**：`_coerce`（`jarvis/tools/router.py`）早已把 string 的 `None` 强制成 `""`。我先前说「计划① 没落地」是**说错了**，这条更正写在 `records/2026-11-13-12-59-10.md` 与 `progress.md`。
