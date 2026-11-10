# 第 1 轮 · 工具返回值文案汉化（探针，pyautogui 打桩，不动真鼠标）

- 时间：2026-11-10 18:02（`.tmp\bats\lab2.log`、`lab3.log`）
- 场景：`.tmp\probe_label2.py` 把 `jarvis.tools.desktop.pyautogui` 替换为 no-op 桩，逐个调用 `dispatch()`，检查返回值文案；再调 3 个只读工具（`get_time` / `get_volume` / `get_system_info`）。未执行任何真实输入，未改音量。
- 期望：用户听到的工具结果全中文；`TOOL_SCHEMAS` 的工具名与参数名保持英文（协议不变）
- 实际（`lab2.log` 原文）：

```
type_text {'text': '你好'} => 已输入文本：你好
press_key {'keys': 'enter'} => 已按下：enter
click_at {'x': 100, 'y': 200, 'button': 'left'} => 已用左键点击 (100, 200)。
click_at {'x': 100, 'y': 200, 'button': 'double'} => 已用双击点击 (100, 200)。
scroll_screen {'direction': 'down', 'amount': 3} => 已滚动：向下 3 格。
scroll_screen {'direction': 'left', 'amount': 3} => 未知滚动方向：left，请用 up/down。
move_mouse {'x': 5, 'y': 6} => 已把鼠标移到 (5, 6)。
media_control {'action': 'zzz'} => 未知媒体操作：zzz，请用 play/pause/next/previous/mute。
power_command {'action': 'zzz'} => 未知电源操作：zzz，请用 shutdown/restart/sleep。
set_clipboard {'text': 'abc'} => 剪贴板已更新。
no_such_tool {} => 未知工具：no_such_tool
read_file {'path': 'C:/Windows/win.ini'} => 工具「读取文件」执行失败：路径不在允许清单内：C:/Windows/win.ini
get_time => 2026-11-10 18:02:02 星期二
get_volume => 当前音量 0%。
get_system_info => CPU 21% | 鍐呭瓨 宸茬敤 14.8/27.8 GB | 纾佺洏C 鍓╀綑 17.7/200 GB
```

- 结果：**PASS（含 1 个当场修掉的缺陷）** — 除最后一行外全中文；`get_system_info` 出现乱码（`鍐呭瓨 宸茬敤`），根因是 `subprocess.run(..., text=True)` 用系统代码页解码 PowerShell 输出。修复：新增 `_ps_utf8()`（`[Console]::OutputEncoding=[System.Text.Encoding]::UTF8` + 按 UTF-8 解码），`get_clipboard` 同步改用。复测（`lab3.log`）：

```
sysinfo => CPU 17% | 内存 已用 14.8/27.8 GB | 磁盘C 剩余 17.7/200 GB
set_clipboard => 剪贴板已更新。
get_clipboard => 测试剪贴板
```

- 备注：协议层不变——`TOOL_SCHEMAS` 的工具名/参数名、`events.db` 与 WS 事件里的 `name` 仍是英文（第 3 轮再验）；`main.py::_exec_tool_with_retry` 的重试判定由 `result.startswith("Tool '")` 改为 `"执行失败：" in result`，否则会静默失去重试。
