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


def _url_keys(url: str) -> set[str]:
    """Title fragments to look for: host, its first subdomain, and any keyword
    query parameter (a page title usually carries the keyword, not the URL)."""
    from urllib.parse import urlparse, unquote
    parsed = urlparse(url)
    keys = {parsed.netloc.lower()}
    if "." in parsed.netloc:
        keys.add(parsed.netloc.split(".")[0].lower())
    for q in parsed.query.split("&"):
        if "=" in q:
            v = unquote(q.split("=", 1)[1])
            if len(v) >= 2:
                keys.add(v.lower())
    return {k for k in keys if k}


def _window_evidence(keys: set[str]):
    """Return ((line, key), window_list) for the first window title carrying one
    of the URL fragments, or (None, window_list)."""
    from jarvis.tools.desktop import get_open_windows, NO_TEXT
    text = get_open_windows()
    if text == NO_TEXT:
        return None, text
    for line in text.splitlines():
        low = line.lower()
        for k in keys:
            if k in low:
                return (line.strip(), k), text
    return None, text


def _browser_exe() -> str | None:
    """Browser executable from the local app table (Chrome first, then Edge)."""
    from jarvis import apps
    for q in ("chrome", "microsoftedge", "msedge", "edge"):
        for row in apps.match(q):
            launch = row.get("launch") or ""
            if launch.lower().endswith(".exe") and os.path.exists(launch):
                return launch
    return None


def open_url(url: str) -> str:
    """Open a URL in the browser and verify a window carries it.

    webbrowser.open() returning True only means the OS handler accepted the URL
    — it does not prove a page opened (rounds 4-6, tests/2026-11-16-11-46-56_cc).
    Launch the browser executable from the app table with the URL as argument,
    then poll the window list for title evidence. Only a real title counts as
    success; otherwise report honestly.
    """
    import time

    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    keys = _url_keys(url)

    exe = _browser_exe()
    if exe:
        # Measured in the user's own environment (outside any sandbox), 2026-11-16
        # 17:22: `chrome.exe --new-window <url>` spawns processes and **no window**.
        # An already-running Chrome instance takes the handoff and opens the URL as
        # a *background tab*, so the window title stays on its active tab. A
        # separate --user-data-dir forces a new instance, which owns its own window
        # and titles it with the page.
        low = exe.lower()
        flags = []
        if low.endswith(("chrome.exe", "msedge.exe")):
            profile = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))), ".tmp", "chrome_profile")
            os.makedirs(profile, exist_ok=True)
            # Measured 2026-11-16 17:49: chrome launched from python hits its own
            # sandbox breakpoint and exits with 0x80000003 (2147483651) — no window
            # at all. --no-sandbox starts it; the dedicated --user-data-dir keeps
            # the weakened-sandbox browser off the user's signed-in profile.
            flags = ["--no-sandbox", "--new-window", f"--user-data-dir={profile}"]
        args = [exe] + flags + [url]
        # No pipes: spawning with captured output fails inside the sandbox
        # (EPERM on piped stdio), and Chromium exits immediately anyway.
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        how = f"已用 {os.path.basename(exe)} 带参数启动 {url}"
        waited = 0.0
        last = ""
        while waited < 12.0:
            hit, last = _window_evidence(keys)
            if hit:
                return f"{how}，并复读到窗口证据：{hit[0]}（匹配关键词 {hit[1]}，用了 {waited:.1f} 秒）"
            time.sleep(1.0)
            waited += 1.0
        return (f"{how}，但 12 秒内没有复读到匹配 {sorted(keys)} 的窗口标题，"
                f"页面可能没有真的打开，请确认。当前窗口列表：{last[:200]}")

    launched = webbrowser.open(url)
    if not launched:
        return f"打开失败：应用表里没有可用的浏览器程序，系统也没有处理器接收这个网址（webbrowser 返回 False）：{url}"
    waited = 0.0
    last = ""
    while waited < 12.0:
        hit, last = _window_evidence(keys)
        if hit:
            return f"已把 {url} 交给系统浏览器处理器（webbrowser 返回 True），并复读到窗口证据：{hit[0]}（匹配关键词 {hit[1]}，用了 {waited:.1f} 秒）"
        time.sleep(1.0)
        waited += 1.0
    return (f"已把 {url} 交给系统浏览器处理器（webbrowser 返回 True），"
            f"但 12 秒内没有复读到匹配 {sorted(keys)} 的窗口标题，"
            f"页面可能没有真的打开，请确认。当前窗口列表：{last[:200]}")


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
