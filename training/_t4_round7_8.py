"""轮 7-8 复测：focus_window 用中文标题，type_text 用剪贴板做证据。"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import time

from jarvis.tools.app_control import open_app
from jarvis.tools.desktop import focus_window, get_open_windows, press_key, type_text
from jarvis.tools.system import get_clipboard

marker = "JARVIS_TOOL_TEST_456"

open_app("notepad")
time.sleep(3.0)
print("窗口列表:", get_open_windows().replace("\n", " | ")[:160])

print("== 轮 7 复测 focus_window（中文标题）")
print(focus_window("记事本"))
time.sleep(1.2)

print("== 轮 8 复测 type_text（剪贴板证据）")
print("清空剪贴板:", get_clipboard()[:40])
type_text(marker)
time.sleep(0.6)
press_key("ctrl+a")
time.sleep(0.4)
press_key("ctrl+c")
time.sleep(0.8)
clip = get_clipboard()
print("剪贴板内容:", repr(clip[:80]))
print("证据：标记在剪贴板里:", marker in clip)

print("中文写入（剪贴板证据）")
type_text("爱莉希雅工具测试")
time.sleep(0.6)
press_key("ctrl+a")
time.sleep(0.4)
press_key("ctrl+c")
time.sleep(0.8)
clip2 = get_clipboard()
print("剪贴板内容:", repr(clip2[:80]))
print("证据：中文在剪贴板里:", "爱莉希雅工具测试" in clip2)
