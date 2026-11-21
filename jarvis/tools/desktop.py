import subprocess
import time
import os
import tempfile
import json
import ctypes
from ctypes import POINTER, wintypes
from pathlib import Path
import pyautogui

from jarvis.tools.system import get_clipboard, set_clipboard

pyautogui.FAILSAFE = False

# Window APIs are declared once here so every tool enumerates windows in
# jarvis' own process. Measured 2026-11-16 15:20: the same script listing
# MainWindowTitle returns 7 windows when run by the harness shell and **0**
# when run as a powershell/pwsh child of python, so any window evidence taken
# through a child process is structurally unavailable to the service — and
# Add-Type is blocked in the sandbox anyway (HB-033).
_USER32 = ctypes.windll.user32
_USER32.IsWindowVisible.argtypes = [ctypes.c_void_p]
_USER32.IsWindowVisible.restype = ctypes.c_bool
_USER32.GetWindowTextLengthW.argtypes = [ctypes.c_void_p]
_USER32.GetWindowTextLengthW.restype = ctypes.c_int
_USER32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
_USER32.GetWindowTextW.restype = ctypes.c_int
_USER32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, POINTER(wintypes.DWORD)]
_USER32.GetWindowThreadProcessId.restype = wintypes.DWORD
_USER32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
_USER32.ShowWindow.restype = ctypes.c_bool
_USER32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
_USER32.SetForegroundWindow.restype = ctypes.c_bool
_ENUM_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_long)


# Single source for the "empty screen" message: read_screen() returns it and
# find_on_screen() compares against it (records/2026-11-10-17-43-08.md — all
# user-facing tool results are Chinese now, protocol names/args stay English).
NO_TEXT = "屏幕上没有可读文字。"


# ──────────────── Typing & Keys ────────────────

def type_text(text: str) -> str:
    """Type text at the current cursor position.

    HB-036（2026-11-13，`tests/2026-11-13-12-59-10_cc/record_8.md`）：老实现无条件
    `return "已输入文本：…"`，而 `pyautogui.write` 对**键盘不可映射的字符**（中文）
    **静默跳过**，不抛异常 —— 于是「爱莉希雅工具测试」一个字都没进记事本（判据：
    记事本标题没有出现 `*` 已修改标记），工具却报成功。现在：全部字符可映射时正常
    键入；含不可映射字符时走**剪贴板粘贴**，并且**先保存、后还原**用户剪贴板
    （剪贴板里可能是别的东西，例如 13:21 时里面是一个 JWT，绝不能弄丢）。
    """
    unmapped = [c for c in text if c not in pyautogui.KEYBOARD_KEYS]
    if not unmapped:
        time.sleep(0.15)
        pyautogui.write(text, interval=0.02)
        return f"已输入文本：{text[:80]}"

    saved = get_clipboard()          # 用户原有内容，测完还原
    set_clipboard(text)
    time.sleep(0.15)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    if saved:
        set_clipboard(saved)
    return f"已输入文本（剪贴板粘贴，{len(unmapped)} 个字符键盘打不出）：{text[:80]}"


def press_key(keys: str) -> str:
    """Press a key or hotkey combo. Example: 'ctrl+shift+esc', 'alt+tab', 'enter'.

    HB-038（2026-11-13，`tests/2026-11-13-12-59-10_cc/record_9.md`）：老实现无条件
    `return "已按下：{keys}"`，`press_key("not_a_key")` 也报成功（键盘上没有任何动作）。
    现在**逐段校验**键名是否在 pyautogui 的键表里，不可识别就返回失败并列出可用键。
    """
    parts = [k.strip() for k in keys.split("+")]
    bad = [p for p in parts if p and p.lower() not in pyautogui.KEYBOARD_KEYS]
    if bad:
        return (f"按键失败：无法识别 {'+'.join(bad)}（可用键如 enter/space/tab/esc/"
                f"ctrl/alt/shift/a-z/0-9）")
    pyautogui.hotkey(*parts)
    return f"已按下：{keys}"


# ──────────────── Mouse Control ────────────────

def click_at(x: int, y: int, button: str = "left") -> str:
    """Click at screen coordinates (x, y). Button: left, right, double."""
    if button == "double":
        pyautogui.doubleClick(x, y)
        label = "双击"
    elif button == "right":
        pyautogui.rightClick(x, y)
        label = "右键"
    else:
        pyautogui.click(x, y)
        label = "左键"
    return f"已用{label}点击 ({x}, {y})。"


def scroll_screen(direction: str, amount: int = 3) -> str:
    """Scroll up or down. Amount = number of scroll steps."""
    if direction.lower() == "up":
        pyautogui.scroll(amount)
        way = "向上"
    elif direction.lower() == "down":
        pyautogui.scroll(-amount)
        way = "向下"
    else:
        return f"未知滚动方向：{direction}，请用 up/down。"
    return f"已滚动：{way} {amount} 格。"


def move_mouse(x: int, y: int) -> str:
    """Move mouse cursor to (x, y) without clicking."""
    pyautogui.moveTo(x, y)
    return f"已把鼠标移到 ({x}, {y})。"


# ──────────────── Screen Reading (OCR) ────────────────

def read_screen() -> str:
    """Take a screenshot and OCR it. Returns all visible text with approximate positions.
    Format: each line is 'text | x,y' where x,y is the center of the text bounding box."""
    tmp = os.path.join(tempfile.gettempdir(), "jarvis_screen.png")
    img = pyautogui.screenshot()
    img.save(tmp)
    return _ocr_image(tmp)


def _ocr_image(image_path: str) -> str:
    """Run Windows OCR on an image file, return text with positions."""
    ps = f"""
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime]

function Await($WinRtTask, $ResultType) {{
    $asTask = [System.WindowsRuntimeSystemExtensions].GetMethod('AsTask', [Type[]]@($WinRtTask.GetType()))
    if (-not $asTask) {{ $asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }} | Select-Object -First 1 }}
    $netTask = $asTask.MakeGenericMethod($ResultType).Invoke($null, @($WinRtTask))
    $netTask.Wait()
    $netTask.Result
}}

$path = '{image_path.replace(chr(92), chr(92)+chr(92))}'
$stream = [System.IO.File]::OpenRead($path)
$randomAccess = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($stream)
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($randomAccess)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
$stream.Dispose()

$output = @()
foreach ($line in $result.Lines) {{
    $words = $line.Words
    if ($words.Count -gt 0) {{
        $x1 = ($words | ForEach-Object {{ $_.BoundingRect.X }}) | Measure-Object -Minimum | Select-Object -Expand Minimum
        $y1 = ($words | ForEach-Object {{ $_.BoundingRect.Y }}) | Measure-Object -Minimum | Select-Object -Expand Minimum
        $x2 = ($words | ForEach-Object {{ $_.BoundingRect.X + $_.BoundingRect.Width }}) | Measure-Object -Maximum | Select-Object -Expand Maximum
        $y2 = ($words | ForEach-Object {{ $_.BoundingRect.Y + $_.BoundingRect.Height }}) | Measure-Object -Maximum | Select-Object -Expand Maximum
        $cx = [int](($x1 + $x2) / 2)
        $cy = [int](($y1 + $y2) / 2)
        $output += "$($line.Text) | $cx,$cy"
    }}
}}
$output -join "`n"
"""
    # HB-034（2026-11-13）：以前用 text=True，读取线程按本机代码页 GBK 解码 OCR 输出，
    # 遇到 0x9c 直接崩在 subprocess._readerthread 里，result.stdout 变 None，
    # 于是 result.stdout.strip() 报 'NoneType' object has no attribute 'strip'
    # （12:13:14 的「屏幕读取失败」根因，日志 start7860_1105.log 1832-1852 行）。
    # 现在拿字节再按 UTF-8 解码（PS 侧已设 [Console]::OutputEncoding = UTF8）。
    result = subprocess.run(
        ["powershell", "-command", ps],
        capture_output=True, text=False, timeout=15,
    )
    text = result.stdout.decode("utf-8", errors="ignore").strip()
    if not text:
        return NO_TEXT
    return text


def find_on_screen(text: str) -> str:
    """Find text on screen using OCR. Returns coordinates of the match, or 'not found'.
    Use click_at() with the returned coordinates to click on it."""
    screen_text = read_screen()
    if screen_text == NO_TEXT:
        return NO_TEXT

    target = text.lower()
    best_match = None
    best_score = 0

    for line in screen_text.split("\n"):
        if " | " not in line:
            continue
        content, coords = line.rsplit(" | ", 1)
        content_lower = content.lower()

        # Exact substring match
        if target in content_lower:
            x, y = coords.split(",")
            return f"已找到「{text}」位于 ({x.strip()}, {y.strip()})，用 click_at 可点击。"

        # Partial word match — score by overlap
        words_target = set(target.split())
        words_content = set(content_lower.split())
        overlap = len(words_target & words_content)
        if overlap > best_score:
            best_score = overlap
            best_match = (content, coords)

    if best_match and best_score > 0:
        content, coords = best_match
        x, y = coords.split(",")
        return f"最接近的匹配：「{content}」位于 ({x.strip()}, {y.strip()})，用 click_at 可点击。"

    # Not found — try scrolling down and searching again
    pyautogui.scroll(-3)  # scroll down
    time.sleep(0.5)
    screen_text_2 = read_screen()
    for line in screen_text_2.split("\n"):
        if " | " not in line:
            continue
        content, coords = line.rsplit(" | ", 1)
        if target in content.lower():
            x, y = coords.split(",")
            return f"滚动后找到「{text}」位于 ({x.strip()}, {y.strip()})，用 click_at 可点击。"

    return f"屏幕上找不到「{text}」（已尝试向下滚动）。"


# ──────────────── Window Management ────────────────

def _visible_windows() -> list[tuple[int, int, str]]:
    """Visible windows with titles, gathered in-process: (hwnd, pid, title)."""
    out: list[tuple[int, int, str]] = []

    def _cb(hwnd, _lparam):
        if not _USER32.IsWindowVisible(hwnd):
            return True
        length = _USER32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        _USER32.GetWindowTextW(hwnd, buf, length + 1)
        pid = wintypes.DWORD(0)
        _USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        out.append((int(hwnd), int(pid.value), buf.value))
        return True

    _USER32.EnumWindows(_ENUM_PROC(_cb), 0)
    return out


def get_open_windows() -> str:
    """Return titles of all open windows, enumerated in jarvis' own process."""
    wins = _visible_windows()
    if not wins:
        return "没有可识别的窗口。"
    return "\n".join(f"{t}（进程 {pid}）" for _, pid, t in wins)


def focus_window(title: str) -> str:
    """Bring a window to the foreground by partial title match, in-process."""
    low = title.lower()
    hit = [(h, p, t) for h, p, t in _visible_windows() if low in t.lower()]
    if not hit:
        return f"找不到标题包含「{title}」的窗口。"
    hwnd, pid, t = hit[0]
# **HB-053 修法①（2026-11-21 13:50）**：聚焦 = 把你的前台交给别的窗口，属于「动你的东西」。
# 2026-11-21 轮 21：`focus_window("")` 空标题匹配任意窗口，把「星之翼」聚焦了（前台是否被改动
# 未证实 —— 你当时在玩游戏，归因照实挂案）。所以只动 jarvis 自起窗口：pid 不在记录文件/profile
# 里 = 不聚焦，照实返回，要动需要你明确授权（Q24 口径）。fail-closed。
    try:
        from jarvis.tools.app_control import _jarvis_windows
        mine = {w[1] for w in _jarvis_windows()}
    except Exception:
        mine = set()
    if pid not in mine:
        return (f"找到窗口「{t}」（进程 {pid}），但它**不是 jarvis 起的窗口**"
                f"（pid 不在 `.tmp/jarvis_browser_pids.json` 与 jarvis profile 里）。"
                f"聚焦它 = 动你的东西，**没有执行**。要动它需要你明确授权。")
    _USER32.ShowWindow(hwnd, 9)  # SW_RESTORE
    if not _USER32.SetForegroundWindow(hwnd):
        return (f"已找到窗口「{t}」（进程 {pid}），但系统拒绝把前台交给它"
                f"（前台锁），请手动点击。")
    return f"已聚焦窗口：{t}（进程 {pid}）"


# ──────────────── Media Control ────────────────

def media_control(action: str) -> str:
    """Control media playback: play, pause, next, previous, mute."""
    key_map = {
        "play": "playpause",
        "pause": "playpause",
        "playpause": "playpause",
        "next": "nexttrack",
        "skip": "nexttrack",
        "previous": "prevtrack",
        "prev": "prevtrack",
        "mute": "volumemute",
    }
    key = key_map.get(action.lower().strip())
    if not key:
        return f"未知媒体操作：{action}，请用 play/pause/next/previous/mute。"
    pyautogui.press(key)
    return f"媒体操作已执行：{action}"


def screenshot(filename: str = "") -> str:
    """Take a screenshot and save it inside the workspace.

    HB-039（2026-11-13，`tests/2026-11-13-12-59-10_cc/record_19.md`）：老实现写到
    `~/Desktop`，服务作为 harness 后台任务启动时**桌面目录禁写** →
    `PermissionError: [Errno 13] Permission denied: 'C:\\Users\\<user>\\Desktop\\xxx.png'`。
    现在写工作区内的 `.tmp/screens/`（沙箱允许），并在文案里给出真实路径与字节数
    （产物留在本机，我不读图 —— 零截图是 Agent 会话侧的约束）。
    """
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    if not filename.endswith(".png"):
        filename += ".png"
    out_dir = Path(__file__).parent.parent.parent / ".tmp" / "screens"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    try:
        img = pyautogui.screenshot()
        img.save(path)
    except Exception as e:
        return f"截图失败：{e}"
    return f"截图已保存：{path}（{path.stat().st_size} 字节）"
