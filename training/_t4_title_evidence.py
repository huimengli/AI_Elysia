"""轮 8 证据升级：用记事本窗口标题做证据（标题随内容变化）。"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import time

from jarvis.tools.app_control import open_app
from jarvis.tools.desktop import focus_window, get_open_windows, press_key, type_text

open_app("notepad")
time.sleep(3.0)
print("初始标题:", get_open_windows().replace("\n", " | ")[:120])
print("focus:", focus_window("记事本"))
time.sleep(1.2)

type_text("ABC123")
time.sleep(1.0)
print("打完 ABC123 后标题:", get_open_windows().replace("\n", " | ")[:120])

print("press_key:", press_key("a"))
time.sleep(0.8)
print("按 a 后标题:", get_open_windows().replace("\n", " | ")[:120])

# 用键盘直接送一个字符（pyautogui press），区分 write 与 press 两条路径
import pyautogui
pyautogui.press("x")
time.sleep(0.8)
print("pyautogui.press('x') 后标题:", get_open_windows().replace("\n", " | ")[:120])
print("鼠标位置:", pyautogui.position())
