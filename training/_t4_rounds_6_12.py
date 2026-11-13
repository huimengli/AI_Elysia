"""20 轮工具测试轮 6-12 驱动：只作用在记事本，证据是文本（零截图消费）。"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import time

from jarvis.tools.app_control import open_app, kill_process
from jarvis.tools.desktop import (click_at, focus_window, get_open_windows,
                                   move_mouse, press_key, read_screen,
                                   scroll_screen, type_text)


def has_notepad() -> str:
    wins = get_open_windows()
    return "Notepad" in wins or "记事本" in wins


print("== 轮 6 open_app + get_open_windows")
print(open_app("notepad"))
time.sleep(3.0)
print("notepad 在窗口列表里:", has_notepad())
print("窗口列表片段:", get_open_windows().replace("\n", " | ")[:200])

print("== 轮 7 focus_window")
print(focus_window("Notepad"))
time.sleep(1.0)

print("== 轮 8 type_text（ASCII 证据 + 中文如实失败）")
marker = "JARVIS_TOOL_TEST_123"
print(type_text(marker))
time.sleep(0.6)
ocr = read_screen()
print("OCR 里含标记:", marker in ocr.replace(" ", ""))
try:
    print("中文输入:", type_text("爱莉希雅工具测试"))
except Exception as e:
    print("中文输入如实失败:", type(e).__name__, e)

print("== 轮 9 press_key")
print(press_key("enter"))
print(press_key("ctrl+end"))

print("== 轮 10 move_mouse + click_at（坐标取自记事本窗口内）")
print(move_mouse(400, 300))
time.sleep(0.3)
import pyautogui
print("鼠标实际位置:", pyautogui.position())
print(click_at(400, 300))

print("== 轮 11 scroll_screen（方向 + 未知方向）")
print(scroll_screen("down", 3))
print(scroll_screen("up", 2))
print(scroll_screen("sideways", 3))

print("== 轮 12 kill_process（只杀记事本 + 不存在进程）")
print(kill_process("notepad"))
time.sleep(1.5)
print("记事本还在吗:", has_notepad())
print(kill_process("zzz_not_exist"))
