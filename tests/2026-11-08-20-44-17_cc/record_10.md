# 轮 10 — 说「你能看得见屏幕吗？」（第 5 句指令）→ `read_screen` 因 GBK 解码崩溃

- **时间**：2026-11-13 12:13:14
- **场景**：唤醒后问「你能看得见屏幕吗？」（触发 `read_screen`）
- **期望**（脚本）：转录正字；屏幕读取返回文本或如实报告失败；无截断
- **实际**：
  ```
  12:13:14 wake  Wake word triggered
  12:13:21 user  你能看得见屏幕吗?
  12:13:31 assistant 屏幕读取失败了，无法获取当前屏幕上的内容。
  ```
  转录正字 **PASS**（整句完整，无截断）。工具侧日志给出根因（两次，`start7860_1105.log` 1832-1852 行）：
  ```
  Exception in thread Thread-69 (_readerthread):
    File "subprocess.py", line 1597, in _readerthread
      buffer.append(fh.read())
  UnicodeDecodeError: 'gbk' codec can't decode byte 0x9c in position 12: illegal multibyte sequence
  [Tool: read_screen] 工具「读取屏幕」执行失败：'NoneType' object has no attribute 'strip'
  ```
- **结果**：转录与「如实报告失败」**PASS**；能力本身 **FAIL**（`read_screen` 不可用）。
- **根因（已定位）**：[jarvis/tools/desktop.py](jarvis/tools/desktop.py:117) 的 `_ocr_image` 用 `subprocess.run(..., text=True)`，读取线程按**本机代码页 GBK** 解码 PowerShell 的 OCR 输出，遇到 `0x9c` 崩在 reader 线程里 → `result.stdout` 变成 `None` → `result.stdout.strip()` 报 `'NoneType' object has no attribute 'strip'`。同文件族已有正确写法 [jarvis/tools/system.py](jarvis/tools/system.py:64) 的 `_ps_utf8`（`text=False` + `decode("utf-8", errors="ignore")`），`_ocr_image` 没用它。
- **备注**：这条与轮 6 的 `'NoneType' object has no attribute 'strip'` **症状同名、根因不同**（轮 6 是 `title=None`，本条是 GBK 解码崩），已分别记入 `hard_bug.md` **HB-034**。顺带：`get_weather` 三次都因 `'ascii' codec can't encode`（中文地名未 URL quote）失败 → **HB-035**。
