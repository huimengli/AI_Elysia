"""轮 8 复测（中文走剪贴板粘贴，标题 * 做证据，剪贴板还原）+ 轮 9（hotkey 证据）。"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import time

from jarvis.tools.app_control import kill_process, open_app
from jarvis.tools.desktop import focus_window, get_open_windows, press_key, type_text
from jarvis.tools.system import get_clipboard, set_clipboard

kill_process("notepad")
time.sleep(1.5)

clip_before = get_clipboard()
print("剪贴板原内容长度:", len(clip_before), "（不打印内容）")

open_app("notepad")
time.sleep(3.0)
print("初始标题:", get_open_windows().replace("\n", " | ")[:120])
print("focus:", focus_window("记事本"))
time.sleep(1.2)

print("type 中文:", type_text("爱莉希雅工具测试"))
time.sleep(1.2)
print("中文后标题:", get_open_windows().replace("\n", " | ")[:120])
clip_after = get_clipboard()
print("剪贴板已还原:", clip_after == clip_before)

print("== 轮 9 press_key 证据（ctrl+a / ctrl+c 把记事本内容送进剪贴板）")
set_clipboard("SENTINEL")
press_key("ctrl+a")
time.sleep(0.4)
press_key("ctrl+c")
time.sleep(0.8)
print("剪贴板（应为记事本内容）:", repr(get_clipboard()[:60]))
print("press_key 未知键:", press_key("not_a_key"))
