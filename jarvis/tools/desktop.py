import subprocess
import time
import os
import tempfile
import json
from pathlib import Path
import pyautogui

from jarvis.tools.system import get_clipboard, set_clipboard

pyautogui.FAILSAFE = False

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

def get_open_windows() -> str:
    """Return titles of all open windows.

    HB-034 家族延伸（2026-11-13，UI 历史里那条「工具「列出窗口」执行失败：'NoneType'
    object has no attribute 'strip'」）：老实现用 `text=True`，PowerShell 输出里有
    **非 GBK 字符**（窗口标题里的 emoji、生僻字、全角符号）时 reader 线程被 GBK 解码崩掉
    → `result.stdout` 变 `None` → `.strip()` 抛 `'NoneType'`。现在显式让 PowerShell 输出
    UTF-8，按 UTF-8 解码，并且**读不到就如实报**，不再假成功。
    """
    result = subprocess.run(
        ["powershell", "-NoProfile", "-command",
         "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
         "Get-Process | Where-Object {$_.MainWindowTitle} | "
         "Select-Object -ExpandProperty MainWindowTitle"],
        capture_output=True, text=False,
    )
    out = result.stdout.decode("utf-8", errors="ignore").strip()
    if result.returncode == 0:
        # 空输出是合法结果（此刻确实没有带标题的窗口），不能算失败
        return out if out else "没有可识别的窗口。"
    err = result.stderr.decode("utf-8", errors="ignore").strip()
    return f"列窗口失败（returncode {result.returncode}）：{err or '无输出'}"


def focus_window(title: str) -> str:
    """Bring a window to the foreground by partial title match.

    HB-033 延伸（2026-11-13）：这里的 `Add-Type -TypeDefinition` 要把源码写进
    `%TEMP%`，而服务作为 harness 后台任务启动时 python 子进程的 `%TEMP%` **禁写**
    （`Access to the path ... denied`）→ 整条聚焦被拒。所以把 `$env:TEMP` 指到工作区
    `.tmp/pscompile`，并 UTF-8 解码输出（`text=True` 会在 reader 线程被 GBK 崩，见
    HB-034）。
    """
    safe = title.replace("'", "''")
    ps_temp = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), ".tmp", "pscompile")
    os.makedirs(ps_temp, exist_ok=True)
    ps = (
        f"$env:TEMP='{ps_temp}'; $env:TMP=$env:TEMP; "
        f"$p = Get-Process | Where-Object {{$_.MainWindowTitle -like '*{safe}*'}} "
        "| Select-Object -First 1; "
        "if ($p) { "
        "Add-Type -TypeDefinition '"
        "using System; using System.Runtime.InteropServices; "
        "public class W { "
        '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); '
        '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n); '
        "}'; "
        "[W]::ShowWindow($p.MainWindowHandle, 9); "
        "[W]::SetForegroundWindow($p.MainWindowHandle) "
        "} else { Write-Output 'not found' }"
    )
    result = subprocess.run(["powershell", "-NoProfile", "-command", ps],
                            capture_output=True, text=False, timeout=20)
    out = result.stdout.decode("utf-8", errors="ignore")
    err = result.stderr.decode("utf-8", errors="ignore").strip()
    if "not found" in out:
        return f"找不到标题包含「{title}」的窗口。"
    if result.returncode != 0:
        return f"聚焦窗口「{title}」失败：{err or '无输出'}"
    return f"已聚焦窗口：{title}"


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
    `PermissionError: [Errno 13] Permission denied: 'C:\\Users\\楼听\\Desktop\\xxx.png'`。
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
