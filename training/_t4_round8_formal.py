"""轮 8 正式判据：新起记事本，分别验 ASCII 与中文能否写入（用标题的 * 修改标记做证据）。"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import time

from jarvis.tools.app_control import kill_process, open_app
from jarvis.tools.desktop import focus_window, get_open_windows, type_text

kill_process("notepad")
time.sleep(1.5)
print("清场后窗口列表:", get_open_windows().replace("\n", " | ")[:120] or "(无)")

open_app("notepad")
time.sleep(3.0)
print("A) 初始标题:", get_open_windows().replace("\n", " | ")[:120])
print("focus:", focus_window("记事本"))
time.sleep(1.2)
print("type ASCII:", type_text("ABC123"))
time.sleep(1.2)
print("A) 之后标题:", get_open_windows().replace("\n", " | ")[:120])

kill_process("notepad")
time.sleep(1.5)
open_app("notepad")
time.sleep(3.0)
print("B) 初始标题:", get_open_windows().replace("\n", " | ")[:120])
print("focus:", focus_window("记事本"))
time.sleep(1.2)
print("type 中文:", type_text("爱莉希雅工具测试"))
time.sleep(1.2)
print("B) 之后标题:", get_open_windows().replace("\n", " | ")[:120])
print("OCR 片段:", get_open_windows().replace("\n", " | ")[:120])
