# 轮 3 — HB-034：`read_screen` 用 UTF-8 解码，不再崩在 reader 线程

- **时间**：2026-11-13 12:30:19
- **场景**：修完后在浏览器输入框打字「读一下屏幕上的文字」（零截图；工具自身写 `jarvis_screen.png`，我不看截图，只读返回文本）
- **期望**（`hard_bug.md` HB-034 方案）：OCR 输出按 UTF-8 解码（PS 侧设 `[Console]::OutputEncoding = UTF8`，Python 侧 `text=False` + `decode("utf-8", errors="ignore")`）；不再出现 `'NoneType' object has no attribute 'strip'`；无文字时返回 `NO_TEXT`
- **实际**：
  - 修前（12:13:14，日志 1832-1852 两次）：`UnicodeDecodeError: 'gbk' codec can't decode byte 0x9c in position 12` 抛在 `subprocess.py:1597 _readerthread` → `result.stdout` 变 `None` → `[Tool: read_screen] 工具「读取屏幕」执行失败：'NoneType' object has no attribute 'strip'`。
  - 修后（日志 59 行，工具返回真实文本）：
    ```
    [Tool: read_screen] ． 实 酎 对 话 与 状 态 显 示 修 一 防 × | 202,25
    ```
- **结果**：**PASS（能力恢复）**，附一条诚实观察：**WinRT OCR 的中文质量差** —— 字间被插空格（`实 酎 对 话 与 状 态 显 示`），且有识别错字（`酎`、`防` 疑为「现」「两」之类）。所以 `find_on_screen` 的**子串匹配在中文上不可靠**（它按空格分词算 overlap，OCR 插空格后基本匹配不上）。
- **备注**：`_ocr_image` 用的 `Add-Type -AssemblyName` 只加载已有程序集，**不需要 Temp 编译**，所以 HB-033 的 TEMP 重定向与这条无关；`desktop.py` 里 `subprocess.run(..., text=True)` 改为 `text=False` + UTF-8 解码，并在 PS 头部加 `[Console]::OutputEncoding=[System.Text.Encoding]::UTF8`。OCR 质量是 WinRT 引擎本身的限制，不是本轮修复引入的。
