"""轮 13-19 驱动：文件 / 代码 / 通知（含空参）/ 计时器 / 亮度 / 电源拒绝分支 / 截图。

证据全部是文本与文件属性，不读图（零截图消费）。
"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import time

from jarvis.tools.code_exec import run_python
from jarvis.tools.file_ops import list_files, read_file, write_file
from jarvis.tools.router import dispatch
from jarvis.tools.system import get_clipboard, set_clipboard
from jarvis.tools.desktop import screenshot

print("== 轮 13 write_file / read_file / list_files（工作区内）")
print(dispatch("write_file", {"path": ".tmp/tooltest.txt", "content": "工具测试\n第二行"}))
print("read_file:", repr(read_file(".tmp/tooltest.txt")))
print("list_files('.tmp') 含 tooltest.txt:", "tooltest.txt" in list_files(".tmp"))
print("越界路径（期望被拒）:", dispatch("read_file", {"path": "C:/Windows/win.ini"}))

print("== 轮 14 run_python")
print("2+2:", repr(run_python("print(2+2)")))
print("中文输出:", repr(run_python("print('爱莉希雅')")))

print("== 轮 15 剪贴板（保存-设置-读取-还原，不打印原内容）")
saved = get_clipboard()
print("原内容长度:", len(saved))
print("set_clipboard:", dispatch("set_clipboard", {"text": "TOOL_TEST_789"}))
print("get_clipboard:", repr(get_clipboard()))
set_clipboard(saved)
print("还原后与原始一致:", get_clipboard() == saved)

print("== 轮 16 show_notification（正常参数 + 空参）")
print("正常:", dispatch("show_notification", {"title": "爱莉希雅", "message": "工具测试通知"}))
time.sleep(1.0)
print("空参（dispatch 传空字典，走 _coerce）:", dispatch("show_notification", {}))
time.sleep(1.0)

print("== 轮 17 set_timer（3 秒）")
print(dispatch("set_timer", {"seconds": 3}))
print("（主线程未被阻塞，等 4 秒让 toast 弹出）")
time.sleep(4.0)

print("== 轮 18 set_brightness（台式机期望走失败分支，带 stderr）")
print(dispatch("set_brightness", {"level": 50}))

print("== 轮 19 power_command 拒绝分支 + screenshot 产物")
print("未知 action:", dispatch("power_command", {"action": "reboot"}))
path = screenshot("jarvis_tool_test.png")
print(path)
p = os.path.join(os.path.expanduser("~"), "Desktop", "jarvis_tool_test.png")
print("文件存在:", os.path.exists(p), "字节:", os.path.getsize(p) if os.path.exists(p) else 0)
