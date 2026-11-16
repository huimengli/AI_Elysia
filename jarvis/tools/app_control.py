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

    # Reuse a window that already carries this URL: each launch with a dedicated
    # --user-data-dir starts its own Chromium instance, so repeated calls opened
    # 2 windows (measured 2026-11-16 19:22, chrome processes 22). Reuse first,
    # with the window title as the evidence, and focus it by the real title only
    # (the listing line carries a 「（进程 N）」 suffix that focus_window cannot match).
    from jarvis.tools.desktop import _visible_windows, focus_window

    for _, _, t in _visible_windows():
        if any(k in t.lower() for k in keys):
            return (f"复用已打开的窗口：{t}（匹配关键词 "
                    f"{sorted(k for k in keys if k in t.lower())[0]}，没有再起新实例）\n"
                    f"{focus_window(t)}")

    # Window limit (user rule 19:47, `<=3`): count first, refuse to start a 4th.
    n = len(_browser_windows())
    if n >= WINDOW_LIMIT:
        titles = "、".join(t for _, _, t in _browser_windows())
        return (f"浏览器窗口已有 {n} 个（上限 {WINDOW_LIMIT}），**拒绝再起新实例**。当前窗口："
                f"{titles}。要开新页请在已有窗口里导航（navigate_url），或先关窗口"
                f"（我起的那批可用 manage_browser_windows 关，需你授权，见 need_user Q29）。")

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
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _launched_pids.append(proc.pid)
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


_VISION_PROMPT = (
    "这是整屏截图（像素坐标与屏幕坐标一致）。"
    "目标：浏览器结果列表里第 {n} 支视频的封面（缩略图）。"
    "只回答一行，格式是 (x,y)，x y 是它中心的整数像素坐标；"
    "该支不可见就只回答「找不到」。不要 JSON、代码块、解释，不要编造坐标。"
)


def _browser_windows() -> list[tuple[int, int, str]]:
    """Visible top-level browser windows (Chrome/Edge), enumerated in-process."""
    from jarvis.tools.desktop import _visible_windows

    out = []
    for h, p, t in _visible_windows():
        low = t.lower()
        if " google chrome" in low or " - microsoft edge" in low or " - edge" in low:
            out.append((h, p, t))
    return out


WINDOW_LIMIT = 3
_launched_pids: list[int] = []  # browser instances jarvis itself started


def manage_browser_windows(close_extra: bool = False) -> str:
    """Count browser windows and enforce the user's limit of 3.

    Closing is a process kill, so it only runs for instances launched with the
    workspace profile `.tmp/chrome_profile` (never the user's signed-in profile),
    and only when `close_extra` is true — which the model sets only after the
    user authorised automatic closing (need_user Q29).
    """
    wins = _browser_windows()
    head = f"浏览器窗口 {len(wins)} 个（上限 {WINDOW_LIMIT}）：" + \
           "、".join(t for _, _, t in wins[:WINDOW_LIMIT + 3])
    if not wins:
        return head
    if not close_extra:
        return head + "。未关闭任何窗口（关闭需你授权）。"

    # Only instances jarvis itself launched (recorded pids), never the user's
    # chrome. Window titles carry no profile marker, so pids are the evidence.
    mine = [(h, p, t) for h, p, t in wins if p in _launched_pids]
    if not mine:
        return head + "。无法从窗口标题认出我起的实例（profile 标记不在标题里），未关闭任何窗口，请手动关。"
    killed, failed = [], []
    for _, p, t in mine[WINDOW_LIMIT:]:
        r = subprocess.run(["taskkill", "/PID", str(p), "/T", "/F"],
                           capture_output=True, text=True)
        (killed if r.returncode == 0 else failed).append(f"{t}（进程 {p}）")
    return (head + f"。关掉超出上限的 {len(mine) - WINDOW_LIMIT} 个（只认 profile 标记 {mark}）："
            + f"成功 {len(killed)}、失败 {len(failed)}。"
            + (f"已关：{'; '.join(killed)}" if killed else "")
            + (f" 失败：{'; '.join(failed)}" if failed else ""))


def navigate_url(url: str) -> str:
    """Navigate an existing browser window to a URL, then verify by title.

    No vision coordinates, no clicks: focus the window, Ctrl+L, type, Enter.
    Verification tracks **the window that was focused** by its handle — a title
    change reported for any other window is a false success (measured 2026-11-16
    19:52: the focused window's title stayed put while an unrelated window's
    title counted as "changed").
    """
    import time

    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    keys = _url_keys(url)
    wins = _browser_windows()
    if not wins:
        return f"没有可导航的浏览器窗口（当前 0 个），{url} 未打开。"
    from jarvis.tools.desktop import focus_window, press_key, type_text, _visible_windows

    # Prefer the window that already carries this site, so the typed URL lands in
    # the page the user is looking at, not in a window of their own.
    hwnd, pid, base = next((w for w in wins if any(k in w[2].lower() for k in keys)), wins[0])
    step = focus_window(base)
    if "找不到" in step:
        return f"导航失败：{step}"
    if "拒绝" in step:
        # System kept the foreground: typing here goes into whatever app the user
        # is looking at, not into this window's address bar. Do not type.
        return f"导航中止：{step}（URL 未敲入任何窗口：{url}）"
    keys_pressed = press_key("ctrl+l")
    time.sleep(0.4)
    typed = type_text(url)
    entered = press_key("enter")

    def title_of(hwnd) -> str | None:
        for h, p, t in _visible_windows():
            if h == hwnd:
                return t
        return None

    waited = 0.0
    while waited < 12.0:
        time.sleep(1.0)
        waited += 1.0
        now = title_of(hwnd)
        if now is None:
            return (f"导航中断：被聚焦的窗口「{base}」（进程 {pid}）在 {waited:.1f} 秒后"
                    f"消失了，无法判定是否跳转（{typed}）。请确认。")
        if now != base:
            return (f"已在被聚焦的窗口导航：基准「{base}」（进程 {pid}）-> 现在「{now}」"
                    f"（{keys_pressed}，{typed}，{entered}，用了 {waited:.1f} 秒）")
    return (f"已把 {url} 送进地址栏（{keys_pressed}，{typed}，{entered}），但 12 秒内"
            f"**被聚焦的窗口**标题没变（仍是「{base}」（进程 {pid}）），页面可能没真的跳转，请确认。")


def first_bilibili_video(keyword: str) -> str:
    """Resolve the first Bilibili result for a keyword to a direct video URL.

    The page embeds its result JSON; the first `bvid` is what the first card
    links to, so no vision coordinates and no clicks are needed. If the network
    is unreachable or the page is blocked by anti-bot, the tool says so.
    """
    import re
    import urllib.parse
    import urllib.request

    q = urllib.parse.quote(keyword)
    url = f"https://search.bilibili.com/all?keyword={q}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120",
        "Referer": "https://www.bilibili.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    try:
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    except Exception as e:
        return (f"取不到 B 站搜索页（{type(e).__name__}: {e}），无法确定第一支视频，"
                f"请确认 jarvis 侧有外网。搜索地址：{url}")
    ids = re.findall(r"\"bvid\":\"(BV[0-9A-Za-z]{5,})\"", html)
    if not ids:
        bvs = re.findall(r"(BV[0-9A-Za-z]{5,})", html)
        ids = bvs
    if not ids:
        return (f"搜索页拿到了 {len(html)} 字节，里面没有 bvid，可能被反爬挡住，"
                f"第一支视频无法确定。地址：{url}")
    return f"第一支视频：https://www.bilibili.com/video/{ids[0]}（搜索页 {len(html)} 字节，共 {len(ids)} 个 bvid）"


def play_first_video(url: str, tries: int = 3) -> str:
    """Reach the first playable item, verifying by window title.

    Route A (preferred, no clicks): resolve the first result to a direct video
    URL and navigate the existing window's address bar. Route B (fallback):
    vision locates the Nth result cover, click, then title check. Every step
    carries evidence; a miss is reported as a miss.
    """
    import time

    from jarvis.tools.desktop import _visible_windows, click_at, focus_window
    from jarvis.tools.vision import ask_vision, _coords

    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    keys = _url_keys(url)
    log = [open_url(url)]

    def titles() -> list[str]:
        return [t for _, _, t in _visible_windows()
                if any(k in t.lower() for k in keys)]

    # Route A: direct URL, no vision, no clicks (the user picked this route after
    # 19:28 — three vision coordinates all landed outside the window).
    kw = ""
    if "keyword=" in url:
        kw = url.split("keyword=", 1)[1].split("&")[0]
    kw = __import__("urllib.parse", (), (), ["unquote"]).unquote(kw)
    base = titles()[0] if titles() else None
    if kw and base:
        found = first_bilibili_video(kw)
        log.append(found)
        if "第一支视频：" in found:
            direct = found.split("第一支视频：", 1)[1].split("（")[0]
            log.append(navigate_url(direct))
            if "现在「" in log[-1]:
                return "\n".join(log)

    base = titles()[0] if titles() else None
    if not base:
        log.append("没有带这个网址的窗口标题，无法作为基准，中止。")
        return "\n".join(log)
    # Bring the page to the front before every capture: screenshots see the whole
    # screen, and a covered window makes the vision coordinates land on other
    # windows (measured 2026-11-16 19:26 — (20,189) is the far-left screen edge).
    log.append(f"聚焦页面：{focus_window(base)}")
    time.sleep(1)

    for n in range(1, tries + 1):
        ans, path, nbytes = ask_vision(_VISION_PROMPT.format(n=n))
        if path is None:
            log.append(f"第 {n} 支：{ans}")
            break
        c = _coords(ans)
        if not c:
            log.append(f"第 {n} 支：视觉没有给出坐标（{ans[:60]}，截图 {path.name}）")
            continue
        log.append(f"第 {n} 支视觉坐标 {c}（截图 {path.name}，{nbytes} 字节）-> {click_at(c[0], c[1])}")
        time.sleep(4)
        now = titles()
        changed = [t for t in now if t != base]
        if changed:
            log.append(f"窗口标题已变：基准「{base}」-> 现在「{changed[0]}」，判定进入视频页")
            return "\n".join(log)
        log.append(f"点击后标题未变（仍是「{base}」），换下一支重试")
    log.append(f"{tries} 次都没有让标题变成视频页，请确认页面上是否真的播放。")
    return "\n".join(log)
