"""Maps LLM tool call names to Python functions and provides tool schemas."""
from jarvis.tools.web_search import search, fetch_page, get_weather
from jarvis.tools.app_control import (open_app, open_url, kill_process,
                                       play_first_video, play_music, manage_browser_windows,
                                       navigate_url, open_site, music_control)
from jarvis.tools.file_ops import read_file, write_file, list_files
from jarvis.tools.code_exec import run_python
from jarvis.tools.system import (
    get_clipboard, set_clipboard, set_volume, get_volume,
    get_system_info, set_brightness, lock_screen, power_command,
    show_notification, set_timer, get_time,
)
from jarvis.tools.desktop import (
    type_text, press_key, get_open_windows, focus_window,
    media_control, screenshot,
    click_at, scroll_screen, move_mouse, read_screen, find_on_screen,
)
from jarvis.tools.vision import describe_screen
from jarvis.tools.browser_cdp import read_page, find_page_text
# `delegate_task` 已从工具面摘掉（2026-11-13 12:59 用户规矩：爱莉希雅不允许启动
# 子智能体）。jarvis/tools/subagent.py 文件保留，只是不再暴露给模型。

TOOL_MAP = {
    # Web
    "web_search":       lambda a: search(a["query"]),
    "fetch_page":       lambda a: fetch_page(a["url"]),
    "open_url":         lambda a: open_url(a["url"]),
    "open_site":        lambda a: open_site(a["site"]),
    "music_control":    lambda a: music_control(a["action"]),
    "play_first_video": lambda a: play_first_video(a["url"]),
    "play_music": lambda a: play_music(a.get("url", ""), a.get("keyword", "")),
    "manage_browser_windows": lambda a: manage_browser_windows(a.get("close_extra", False)),
    "navigate_url":       lambda a: navigate_url(a["url"]),
    "read_page":          lambda a: read_page(a.get("keyword", "")),
    "find_on_page":       lambda a: find_page_text(a["text"]),
    "click_page_text":    lambda a: find_page_text(a["text"], click=True),
    "get_weather":      lambda a: get_weather(a.get("location", "")),
    "get_time":         lambda _: get_time(),
    # Apps & processes
    "open_app":         lambda a: open_app(a["name"]),
    "kill_process":     lambda a: kill_process(a["name"]),
    # Desktop automation — vision & mouse
    "read_screen":      lambda _: read_screen(),
    "describe_screen":  lambda a: describe_screen(a["question"]),
    "find_on_screen":   lambda a: find_on_screen(a["text"]),
    "click_at":         lambda a: click_at(int(a["x"]), int(a["y"]), a.get("button", "left")),
    "scroll_screen":    lambda a: scroll_screen(a["direction"], int(a.get("amount", 3))),
    "move_mouse":       lambda a: move_mouse(int(a["x"]), int(a["y"])),
    # Desktop automation — windows & typing
    "focus_window":     lambda a: focus_window(a["title"]),
    "get_open_windows": lambda _: get_open_windows(),
    "type_text":        lambda a: type_text(a["text"]),
    "press_key":        lambda a: press_key(a["keys"]),
    "media_control":    lambda a: media_control(a["action"]),
    "screenshot":       lambda a: screenshot(a.get("filename", "")),
    # Files
    "read_file":        lambda a: read_file(a["path"]),
    "write_file":       lambda a: write_file(a["path"], a["content"]),
    "list_files":       lambda a: list_files(a["path"]),
    # Code
    "run_python":       lambda a: run_python(a["code"]),
    # Clipboard
    "get_clipboard":    lambda _: get_clipboard(),
    "set_clipboard":    lambda a: set_clipboard(a["text"]),
    # System
    "set_volume":       lambda a: set_volume(int(a["level"])),
    "get_volume":       lambda _: get_volume(),
    "get_system_info":  lambda _: get_system_info(),
    "set_brightness":   lambda a: set_brightness(int(a["level"])),
    "lock_screen":      lambda _: lock_screen(),
    "power_command":    lambda a: power_command(a["action"]),
    # Notifications & timers
    "show_notification": lambda a: show_notification(a["title"], a["message"]),
    "set_timer":        lambda a: set_timer(int(a["seconds"]), a.get("message", "定时到了！")),
}

# Chinese display names for spoken / on-screen reports (records/2026-11-09-21-55-14.md).
# The English name stays the schema/protocol identity; this map is only for 播报与 UI.
TOOL_LABELS = {
    "web_search": "联网搜索（打开浏览器，baidu 首选 bing 兜底）",
    "open_site": "打开指定对象（浏览器/b站/github/自定义）",
    "music_control": "播放控制（暂停/恢复/关闭音乐）",
    "fetch_page": "读取网页",
    "open_url": "打开网址",
    "play_first_video": "播放第一支视频",
    "play_music": "播放音乐（关弹幕/最低档/播完关窗）",
    "manage_browser_windows": "管理浏览器窗口",
    "navigate_url": "导航网址",
    "read_page": "读取我起窗口的页面文本（CDP，无 OCR）",
    "find_on_page": "页面文本查找（CDP，无 OCR）",
    "click_page_text": "点击页面文字（CDP 受信点击）",
    "get_weather": "查天气",
    "get_time": "看时间",
    "open_app": "打开应用",
    "kill_process": "结束进程",
    "read_screen": "读取屏幕",
    "describe_screen": "看屏幕画面",
    "find_on_screen": "屏幕查找",
    "click_at": "点击坐标",
    "scroll_screen": "滚动屏幕",
    "move_mouse": "移动鼠标",
    "focus_window": "聚焦窗口",
    "get_open_windows": "列出窗口",
    "type_text": "输入文本",
    "press_key": "按下按钮",
    "media_control": "媒体控制",
    "screenshot": "截图",
    "read_file": "读取文件",
    "write_file": "写入文件",
    "list_files": "列出文件",
    "run_python": "运行代码",
    "get_clipboard": "读取剪贴板",
    "set_clipboard": "写入剪贴板",
    "set_volume": "设置音量",
    "get_volume": "查看音量",
    "get_system_info": "系统信息",
    "set_brightness": "设置亮度",
    "lock_screen": "锁定屏幕",
    "power_command": "电源操作",
    "show_notification": "发送通知",
    "set_timer": "设置计时器",
}


def tool_label(name: str) -> str:
    """Chinese display name for a tool; falls back to the English name."""
    return TOOL_LABELS.get(name, name)

TOOL_SCHEMAS = [
    # --- Web ---
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search = **open a browser search page**. baidu first; if baidu blocks or lands off the results page, bing is used as fallback. jarvis opens its own browser window (profile-verified); results are read afterwards with read_screen / find_on_screen. Returns the engine, URL, page title and address as evidence; a miss is reported as a miss.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}},

    {"type": "function", "function": {
        "name": "open_site",
        "description": "Open a named object in jarvis' own browser window: 浏览器/browser, b站/bilibili/bili, github, 百度/baidu, bing, or a user-defined name from config.yaml `sites:` (the user's custom objects). Chinese, English and pinyin names all match; user names take priority. If the name is not in the map it says so plainly and opens nothing — do not invent a URL. Desktop apps (e.g. 微信) go through open_app, not this.",
        "parameters": {"type": "object", "properties": {
            "site": {"type": "string",
                     "description": "The name exactly as heard (浏览器, b站, github, 我的服务器…). Do not translate."}},
            "required": ["site"]}}},

    {"type": "function", "function": {
        "name": "music_control",
        "description": "Playback control on jarvis' own window only. action=pause → 暂停当前播放的视频 (verified by reading `video.paused` back through CDP), action=resume → 恢复播放, action=close → 关闭音乐 by closing the browser window jarvis started. Only pids jarvis recorded for itself are ever killed; the user's windows are never touched. Reports the readback, not a guess.",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string",
                       "enum": ["pause", "resume", "close"],
                       "description": "pause 暂停播放 / resume 恢复播放 / close 关闭音乐"}},
            "required": ["action"]}}},

    {"type": "function", "function": {
        "name": "fetch_page",
        "description": "Fetch a URL and return plain text content.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string"}}, "required": ["url"]}}},

    {"type": "function", "function": {
        "name": "open_url",
        "description": "Open a URL in the browser. Use this to reach a web page — not by launching the browser app and typing.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string",
                    "description": "Full URL including https://."},
            }, "required": ["url"]}}},

    {"type": "function", "function": {
        "name": "play_first_video",
        "description": "Reach the first playable item on a results page and verify it: resolve the first result to a direct URL and navigate the window, then check the window title changed. Falls back to vision coordinates and a click only when the URL cannot be resolved. Returns every step with evidence, so a miss is reported as a miss. Do NOT use this to play a song — songs must go through play_music, which turns off the danmaku, sets the lowest quality, starts playback with a trusted click, and closes jarvis' own window at the end.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string",
                    "description": "Page to open."},
            }, "required": ["url"]}}},

    {"type": "function", "function": {
        "name": "play_music",
        "description": "The ONLY tool for playing a song on Bilibili. Pass the song title as keyword (Chinese is fine) and it resolves the most-played (order=play) result through the Bilibili API, navigates jarvis' own window straight to that BV URL (no vision, no clicks), turns OFF the danmaku, sets the lowest quality (item labelled 360P 流畅, width 640, height follows the source aspect), starts playback with a trusted click on 播放/暂停 (video.play() alone is blocked by Chrome autoplay policy), resets to 0:00 because Bilibili resumes at the last watched position, then polls: playback time must advance, and reaching the end is signalled by the BV id in the page URL changing (连播 fires at the end). When the song ends, the window jarvis started is killed (only pids jarvis recorded at launch; the user's own windows are never touched). Returns every step with evidence; a miss is reported as a miss. Pass a direct BV URL as url when you already have one. **Call it ONCE per request** — the returned text already covers 解析/导航/关弹幕/最低分辨率/时间前进/播完/关窗; calling it a second time replays the song from 0:00 (measured 11:12: the model called play_music twice in one request, keyword then url, and played the same song twice).",
        "parameters": {"type": "object", "properties": {
            "keyword": {"type": "string",
                        "description": "Song title to search, e.g. 月声尽,心灯明. Preferred for song requests."},
            "url": {"type": "string",
                    "description": "Optional direct video URL (https://www.bilibili.com/video/BV…) if already resolved."},
            }, "required": []}}},

    {"type": "function", "function": {
        "name": "manage_browser_windows",
        "description": "Count the browser windows jarvis started itself against the limit of 3 (the user's own windows are not counted), and close the extras. Returns titles and the result of any kill.",
        "parameters": {"type": "object", "properties": {
            "close_extra": {"type": "boolean",
                            "description": "true to close windows beyond the limit. Only pids jarvis recorded at launch are killed — the user's own browser is never a target (authorised 2026-11-16 20:09)."}},
            "required": []}}},

    {"type": "function", "function": {
        "name": "navigate_url",
        "description": "Send an existing browser window to a URL by address bar (focus, Ctrl+L, type, Enter), then verify the window title changed. No vision coordinates, no clicks.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string",
                    "description": "Full URL including https://. Use the direct video URL when playing a song."},
            }, "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "Get current weather for a location. Leave location empty for auto-detect.",
        "parameters": {"type": "object", "properties": {
            "location": {"type": "string", "description": "City name or empty for auto-detect"}},
            "required": []}}},

    # --- Apps & processes ---
    {"type": "function", "function": {
        "name": "open_app",
        "description": "Open an installed **desktop program** on this machine (微信, 记事本, notepad, chrome.exe). Matches a local app table of ~227 entries (Start Menu + system apps), so Chinese, English and pinyin names work; several close matches are reported as candidates instead of being picked silently. **Do not use it for web pages**: 打开浏览器 / 打开b站 / 打开github / 打开自定义站点 go through `open_site`; never improvise a page by typing text into whatever window is focused.",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string",
                     "description": "Pass the name exactly as heard: Chinese (记事本), English (notepad, chrome) or pinyin (jishiben). Do not translate or substitute a name the user did not say."},
            }, "required": ["name"]}}},

    {"type": "function", "function": {
        "name": "kill_process",
        "description": "Kill/close a running process by name (e.g. chrome, spotify, discord).",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string",
                     "description": "Process name in English (notepad, mspaint). Non-Latin names are stripped and the kill fails, so use the process name, not the window title."},
            }, "required": ["name"]}}},

    # --- Screen vision & mouse (AGENTIC) ---
    {"type": "function", "function": {
        "name": "read_screen",
        "description": "OCR the screen. Returns all visible text with coordinates: 'text | x,y'. Use to see what's on screen before acting.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "describe_screen",
        "description": "Look at the whole screen with the vision model. Returns the model's answer, including integer x,y to pass to click_at. Use it to find a target that is a picture — video cover, play button, icon, layout — where OCR text cannot identify it.",
        "parameters": {"type": "object", "properties": {
            "question": {"type": "string",
                         "description": "In Chinese, name the picture to find, e.g. 第一个视频的封面位置"}},
            "required": ["question"]}}},

    {"type": "function", "function": {
        "name": "find_on_screen",
        "description": "Find text on screen via OCR. Returns coordinates to click. Use with click_at.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"}}, "required": ["text"]}}},

    {"type": "function", "function": {
        "name": "click_at",
        "description": "Click at screen coordinates (x, y). Button: left (default), right, double. If the click was meant to open a page, verify with get_open_windows: the window title must change to the page's title — if it is unchanged the point missed the target, so ask describe_screen for the target again and click once more.",
        "parameters": {"type": "object", "properties": {
            "x": {"type": "integer", "description": "Screen pixel x from describe_screen's 点击坐标"},
            "y": {"type": "integer", "description": "Screen pixel y from describe_screen's 点击坐标"},
            "button": {"type": "string", "enum": ["left", "right", "double"]}},
            "required": ["x", "y"]}}},

    {"type": "function", "function": {
        "name": "scroll_screen",
        "description": "Scroll up or down. Amount = number of scroll steps (default 3).",
        "parameters": {"type": "object", "properties": {
            "direction": {"type": "string", "enum": ["up", "down"]},
            "amount": {"type": "integer"}},
            "required": ["direction"]}}},

    {"type": "function", "function": {
        "name": "move_mouse",
        "description": "Move mouse cursor to (x, y) without clicking.",
        "parameters": {"type": "object", "properties": {
            "x": {"type": "integer"},
            "y": {"type": "integer"}},
            "required": ["x", "y"]}}},

    # --- Desktop automation ---
    {"type": "function", "function": {
        "name": "focus_window",
        "description": "Bring a window to foreground by partial title.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string",
                      "description": "A fragment of the title as shown on screen. Titles are localized: Notepad shows 「无标题 - 记事本」, so use Chinese fragments (记事本), not the process name."},
            }, "required": ["title"]}}},

    {"type": "function", "function": {
        "name": "get_open_windows",
        "description": "List all open window titles.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "type_text",
        "description": "Type text at current cursor position.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"}}, "required": ["text"]}}},

    {"type": "function", "function": {
        "name": "press_key",
        "description": "Press key/hotkey: ctrl+c, alt+tab, win+d, enter, escape, ctrl+shift+esc.",
        "parameters": {"type": "object", "properties": {
            "keys": {"type": "string"}}, "required": ["keys"]}}},

    {"type": "function", "function": {
        "name": "media_control",
        "description": "Media playback: play, pause, next, previous, mute.",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string"}}, "required": ["action"]}}},

    {"type": "function", "function": {
        "name": "screenshot",
        "description": "Take a screenshot, saves to Desktop.",
        "parameters": {"type": "object", "properties": {
            "filename": {"type": "string"}}, "required": []}}},

    # --- Files ---
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file (Documents or Desktop only).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},

    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write text to file (Documents or Desktop only).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"}}, "required": ["path", "content"]}}},

    {"type": "function", "function": {
        "name": "list_files",
        "description": "List files in directory (Documents or Desktop only).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},

    # --- Code ---
    {"type": "function", "function": {
        "name": "run_python",
        "description": "Execute Python code, returns stdout/stderr.",
        "parameters": {"type": "object", "properties": {
            "code": {"type": "string"}}, "required": ["code"]}}},

    # --- Clipboard ---
    {"type": "function", "function": {
        "name": "get_clipboard",
        "description": "Get clipboard text.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "set_clipboard",
        "description": "Set clipboard text.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"}}, "required": ["text"]}}},

    # --- System ---
    {"type": "function", "function": {
        "name": "set_volume",
        "description": "Set system volume 0-100.",
        "parameters": {"type": "object", "properties": {
            "level": {"type": "integer"}}, "required": ["level"]}}},

    {"type": "function", "function": {
        "name": "get_volume",
        "description": "Get current system volume.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "get_time",
        "description": "Get the current local date, clock time and weekday. Use this for 现在几点 / 今天几号 / 日期 questions — not get_weather.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "get_system_info",
        "description": "Get CPU, RAM, and disk usage stats.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "set_brightness",
        "description": "Set screen brightness 0-100 (laptops only).",
        "parameters": {"type": "object", "properties": {
            "level": {"type": "integer"}}, "required": ["level"]}}},

    {"type": "function", "function": {
        "name": "lock_screen",
        "description": "Lock the workstation.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "power_command",
        "description": "Shutdown, restart, or sleep the PC.",
        "parameters": {"type": "object", "properties": {
            "action": {"type": "string", "enum": ["shutdown", "restart", "sleep"]}},
            "required": ["action"]}}},

    # --- Notifications & timers ---
    {"type": "function", "function": {
        "name": "show_notification",
        "description": "Show a Windows toast notification.",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"},
            "message": {"type": "string"}}, "required": ["title", "message"]}}},

    {"type": "function", "function": {
        "name": "set_timer",
        "description": "Set a timer (in seconds) that shows a notification when done.",
        "parameters": {"type": "object", "properties": {
            "seconds": {"type": "integer"},
            "message": {"type": "string"}}, "required": ["seconds"]}}},

    {"type": "function", "function": {
        "name": "read_page",
        "description": "Read the text of **my own** browser window via CDP DOM (no OCR, no vision, no coordinates): returns page title, address, and the first 1200 characters of `innerText`. Use it to see search results / page content after `web_search`/`open_site`. If CDP is unreachable it reports that honestly (no page = no reading).",
        "parameters": {"type": "object", "properties": {
            "keyword": {"type": "string", "description": "Optional keyword to pick which of my tabs to read; omit for the active one."}},
            "required": []}}},

    {"type": "function", "function": {
        "name": "find_on_page",
        "description": "Locate text inside **my own** browser window by DOM text matching (not OCR). Returns up to 5 hits with page CSS coordinates, plus the list of text the page actually shows if nothing matches. Use this instead of `find_on_screen`, whose OCR engine is unavailable on this machine.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"}}, "required": ["text"]}}},

    {"type": "function", "function": {
        "name": "click_page_text",
        "description": "Click the first DOM element in **my own** browser window whose text matches. Trusted CDP mouse events at `getBoundingClientRect` coordinates (page CSS px, not vision coordinates); afterwards it reads back title + address as evidence. Use for links/buttons in my window; never for desktop apps.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"}}, "required": ["text"]}}},

    # Subagent 已摘掉：delegate_task 不再暴露给模型（2026-11-13 12:59 规矩）
]


_SCHEMA_PARAMS = {s["function"]["name"]: s["function"].get("parameters", {}).get("properties", {})
                   for s in TOOL_SCHEMAS}


# HB-040 收尾（records/2026-11-21-10-39-00.md 第 8 项，轮 20 审计）：TOOL_MAP 是 lambda
# 直取键（`lambda a: f(a["url"])`），模型省略必填键时 `a["url"]` 直接 KeyError → 「执行失败」
# 灌回模型（2026-11-08 关掉的幻觉通道又从这条缝漏）。规则照实分两档：
#   - 必填**字符串**缺：灌 ""，让工具走自己的如实分支（power_command("") → 未知电源操作；
#     kill_process("") → taskkill 失败；open_url("") → 「输入里没有 URL」）。
#   - 必填**数字/布尔**缺（click_at 的 x/y、move_mouse、set_volume、set_brightness、
#     set_timer 的 seconds）：**不注入、不执行**，返回缺参说明。灌 0 会把音量/亮度真的调成
#     0、把鼠标真的挪到 (0,0) —— 那是真实副作用，不是「让工具跑起来」。
_SCHEMA_REQUIRED = {s["function"]["name"]: set(s["function"].get("parameters", {}).get("required", []))
                    for s in TOOL_SCHEMAS}


def _coerce(tool_name: str, tool_args: dict) -> dict:
    """Force tool arguments to the types the schema declares.

    The 2B model emits {"title": null} and omits required string args, which made
    tools die with 'NoneType' object has no attribute 'strip' — that failure string
    was then fed back to the model as its "fact" (events.db rows 242/245,
    records/2026-11-08-20-44-17.md). Coercing to ""/0 keeps the tool running and
    keeps the hallucination channel shut.

    **HB-040 fix (2026-11-17, records/2026-11-17-13-25-00.md)**: the old loop wrote a
    value for **every** schema property, so a key the model **omitted** arrived at the
    function as `""`/`0`/`False` — which overrode the function's own Chinese default.
    Measured: `set_timer(seconds, message="定时到了！")` (system.py L248) announced an
    **empty string** when the model left `message` out. A missing key now stays missing
    so the function default applies; an explicit `null` is still coerced, because
    feeding `None` into a string tool is the crash that opened the hallucination channel.
    """
    props = _SCHEMA_PARAMS.get(tool_name, {})
    out = dict(tool_args) if isinstance(tool_args, dict) else {}
    # 必填字符串缺：灌 ""（让工具走自己的如实分支），见上方规则
    for key in _SCHEMA_REQUIRED.get(tool_name, ()):  
        if key not in out and props.get(key, {}).get("type") == "string":
            out[key] = ""
    for key, spec in props.items():
        if key not in out:
            continue  # model omitted it: keep the function's own default, do not inject
        t = spec.get("type")
        v = out[key]
        if t == "string":
            out[key] = "" if v is None else str(v)
        elif t == "integer":
            try:
                out[key] = int(v)
            except (TypeError, ValueError):
                out[key] = 0
        elif t == "number":
            try:
                out[key] = float(v)
            except (TypeError, ValueError):
                out[key] = 0.0
        elif t == "boolean":
            out[key] = bool(v)
    return out


def dispatch(tool_name: str, tool_args: dict) -> str:
    """Execute a named tool and return string result."""
    fn = TOOL_MAP.get(tool_name)
    if fn is None:
        return f"未知工具：{tool_label(tool_name)}"
    # 必填数字/布尔缺：**不执行**（灌 0 是真实副作用），把缺参事实直说给模型
    missing = [k for k in _SCHEMA_REQUIRED.get(tool_name, ())
               if k not in tool_args and _SCHEMA_PARAMS.get(tool_name, {}).get(k, {}).get("type") != "string"]
    if missing:
        return (f"工具「{tool_label(tool_name)}」缺必填参数 {missing}（不是字符串，灌 0 就是真实副作用："
                f"音量/亮度/鼠标坐标会被真的改掉），**没有执行任何动作**。")
    try:
        return str(fn(_coerce(tool_name, tool_args)))
    except Exception as e:
        return f"工具「{tool_label(tool_name)}」执行失败：{e}"