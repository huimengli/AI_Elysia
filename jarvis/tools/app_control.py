import subprocess
import os
import shutil
import time
import webbrowser

from jarvis.apps import launch as apps_launch, match as apps_match, running as apps_running, total as apps_total
from jarvis.apps import fuzzy_open as apps_fuzzy

_USER = os.environ.get("USERNAME", "User")

APP_MAP = {
    # Browsers
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    # Communication
    "discord": rf"C:\Users\{_USER}\AppData\Local\Discord\Update.exe",
    "telegram": rf"C:\Users\{_USER}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "slack": rf"C:\Users\{_USER}\AppData\Local\slack\slack.exe",
    "teams": rf"C:\Users\{_USER}\AppData\Local\Microsoft\Teams\current\Teams.exe",
    "zoom": rf"C:\Users\{_USER}\AppData\Roaming\Zoom\bin\Zoom.exe",
    # Dev tools
    "vscode": "code",
    "vs code": "code",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "git bash": rf"C:\Program Files\Git\git-bash.exe",
    # Media
    "spotify": rf"C:\Users\{_USER}\AppData\Roaming\Spotify\Spotify.exe",
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    # Gaming
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",
    "epic games": r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
    # Productivity
    "notepad": "notepad.exe",
    "notepad++": r"C:\Program Files\Notepad++\notepad++.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "paint": "mspaint.exe",
    "snipping tool": "SnippingTool.exe",
    # System
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "calculator": "calc.exe",
    "settings": "ms-settings:",
    "control panel": "control.exe",
}

_FALLBACKS = {
    "chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
}

# Discord needs --processStart flag
_ARGS = {
    "discord": ["--processStart", "Discord.exe"],
}


def open_app(name: str) -> str:
    """Open an application. 三段次序（records/2026-11-13-13-46-12.md）：

    ① **先匹配应用表** `apps`（227 条，扫开始菜单 + 系统应用别名，规范化后精确→子串）；
    ② **不匹配才走其它路径**（`APP_MAP` / 补 `.exe` / `PATH`）；
    ③ 启动后**复读到进程出现才算成功**（20 轮抓出 5 条「跑了就算成功」，`Popen` 不抛异常
    不等于应用存在 —— `Popen('打开记事本')` 这种直接抛，而 `Popen('code')` 在没装时也会抛，
    但 `Popen` 成功启动一个立刻退出的程序老实现也算成功）。多候选**如实列出，不静默乱选**。
    """
    cands = apps_match(name)
    if len(cands) > 1:
        # **同一个程序**判据是 exe 文件名，不是 launch 字符串：`Notepad`（开始菜单
        # `C:\Windows\system32\notepad.exe`）和 `记事本`（别名表 `notepad.exe`）是同一个程序，
        # 14:17 服务级实测把这两种写法当成「2 个候选」，让用户做了一道不存在的选择题。
        stems = {os.path.basename(c["launch"].lower()).removesuffix(".exe") for c in cands}
        if len(stems) == 1:  # 别名同源，指向同一个程序，不算歧义
            best = max(cands, key=lambda c: c["hits"])  # 优先用户用过的那条
            ok, msg = apps_launch(best)
            return msg + f"（列表里 {len(cands)} 条名字都指向它）"
        names = "、".join(c["name"] for c in cands)
        return (f"「{name}」在应用列表里有 {len(cands)} 个候选：{names}。"
                f"请说清楚要打开哪一个，我不会替你选。")
    if len(cands) == 1:
        ok, msg = apps_launch(cands[0])
        return msg
    # ①b 音近/形近层（ASR 名称听不准；records/2026-11-13-13-46-12.md 追加节）
    status, msg = apps_fuzzy(name)
    if status in ("opened", "candidates"):
        return msg
    # ② 不匹配 → 其它路径
    key = name.lower().strip()
    exe = APP_MAP.get(key, key)
    if not exe.lower().endswith(".exe") and not exe.endswith(":") and os.sep not in exe:
        # 裸命令名：补 .exe 并在 PATH 里找
        found = shutil.which(exe) or shutil.which(exe + ".exe")
        exe = found or exe
    if not (os.path.exists(exe) or shutil.which(exe) or exe.endswith(":")):
        return (f"打不开「{name}」：应用列表（{apps_total()} 条）里没有它，"
                f"本机也找不到可执行文件 {exe}。")
    try:
        subprocess.Popen([exe] + _ARGS.get(key, []))
    except Exception as e:
        fallback = _FALLBACKS.get(key)
        if fallback:
            try:
                subprocess.Popen([fallback] + _ARGS.get(key, []))
                exe = fallback
            except Exception:
                return f"打不开「{name}」：{e}"
        else:
            return f"打不开「{name}」：{e}"
    stem = os.path.splitext(os.path.basename(exe))[0].lower()
    waited = 0.0
    while waited < 6.0:
        proc = apps_running(exe)
        if proc:
            return f"已打开：{name}（应用列表里没有，走其它路径，复读确认进程 {proc}）"
        time.sleep(0.5)
        waited += 0.5
    return f"启动了「{name}」但复读到不了进程 {stem}，不能算成功（{exe}）。"


def open_url(url: str) -> str:
    """Open a URL in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"已在浏览器打开：{url}"


def kill_process(name: str) -> str:
    """Kill a process by name (e.g. 'spotify', 'chrome')."""
    # Sanitize: only allow alphanumeric, dots, spaces, hyphens
    safe = "".join(c for c in name if c.isalnum() or c in ".-_ ")
    result = subprocess.run(
        ["taskkill", "/IM", f"{safe}.exe", "/F"],
        capture_output=True, text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        return f"已结束进程：{name}"
    return f"结束进程「{name}」失败：{output}"
