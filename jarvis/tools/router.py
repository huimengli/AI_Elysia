"""Maps LLM tool call names to Python functions and provides tool schemas."""
from jarvis.tools.web_search import search, fetch_page, get_weather
from jarvis.tools.app_control import open_app, open_url, kill_process
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
from jarvis.tools.subagent import delegate_task

TOOL_MAP = {
    # Web
    "web_search":       lambda a: search(a["query"]),
    "fetch_page":       lambda a: fetch_page(a["url"]),
    "open_url":         lambda a: open_url(a["url"]),
    "get_weather":      lambda a: get_weather(a.get("location", "")),
    "get_time":         lambda _: get_time(),
    # Apps & processes
    "open_app":         lambda a: open_app(a["name"]),
    "kill_process":     lambda a: kill_process(a["name"]),
    # Desktop automation — vision & mouse
    "read_screen":      lambda _: read_screen(),
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
    "set_timer":        lambda a: set_timer(int(a["seconds"]), a.get("message", "Timer done!")),
    # Subagent
    "delegate_task":    lambda a: delegate_task(a["task"], a.get("context", "")),
}

# Chinese display names for spoken / on-screen reports (records/2026-11-09-21-55-14.md).
# The English name stays the schema/protocol identity; this map is only for 播报与 UI.
TOOL_LABELS = {
    "web_search": "联网搜索",
    "fetch_page": "读取网页",
    "open_url": "打开网址",
    "get_weather": "查天气",
    "get_time": "看时间",
    "open_app": "打开应用",
    "kill_process": "结束进程",
    "read_screen": "读取屏幕",
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
    "delegate_task": "委派任务",
}


def tool_label(name: str) -> str:
    """Chinese display name for a tool; falls back to the English name."""
    return TOOL_LABELS.get(name, name)

TOOL_SCHEMAS = [
    # --- Web ---
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the web. Returns top result snippets.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}},

    {"type": "function", "function": {
        "name": "fetch_page",
        "description": "Fetch a URL and return plain text content.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string"}}, "required": ["url"]}}},

    {"type": "function", "function": {
        "name": "open_url",
        "description": "Open a URL in the default browser.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string"}}, "required": ["url"]}}},

    {"type": "function", "function": {
        "name": "get_weather",
        "description": "Get current weather for a location. Leave location empty for auto-detect.",
        "parameters": {"type": "object", "properties": {
            "location": {"type": "string", "description": "City name or empty for auto-detect"}},
            "required": []}}},

    # --- Apps & processes ---
    {"type": "function", "function": {
        "name": "open_app",
        "description": "Open app by name: chrome, firefox, edge, brave, discord, telegram, slack, teams, zoom, vscode, terminal, cmd, powershell, git bash, spotify, vlc, steam, epic games, notepad, notepad++, word, excel, powerpoint, paint, snipping tool, explorer, task manager, calculator, settings, control panel.",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string"}}, "required": ["name"]}}},

    {"type": "function", "function": {
        "name": "kill_process",
        "description": "Kill/close a running process by name (e.g. chrome, spotify, discord).",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string"}}, "required": ["name"]}}},

    # --- Screen vision & mouse (AGENTIC) ---
    {"type": "function", "function": {
        "name": "read_screen",
        "description": "OCR the screen. Returns all visible text with coordinates: 'text | x,y'. Use to see what's on screen before acting.",
        "parameters": {"type": "object", "properties": {}}}},

    {"type": "function", "function": {
        "name": "find_on_screen",
        "description": "Find text on screen via OCR. Returns coordinates to click. Use with click_at.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"}}, "required": ["text"]}}},

    {"type": "function", "function": {
        "name": "click_at",
        "description": "Click at screen coordinates (x, y). Button: left (default), right, double.",
        "parameters": {"type": "object", "properties": {
            "x": {"type": "integer"},
            "y": {"type": "integer"},
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
            "title": {"type": "string"}}, "required": ["title"]}}},

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

    # --- Subagent ---
    {"type": "function", "function": {
        "name": "delegate_task",
        "description": "Delegate a subtask to a fast local AI model (Ollama). Use for: summarizing text, reformatting data, writing boilerplate, simple Q&A. Provide the task and optional context.",
        "parameters": {"type": "object", "properties": {
            "task": {"type": "string", "description": "What the subagent should do"},
            "context": {"type": "string", "description": "Optional context/data for the subtask"}},
            "required": ["task"]}}},
]


_SCHEMA_PARAMS = {s["function"]["name"]: s["function"].get("parameters", {}).get("properties", {})
                   for s in TOOL_SCHEMAS}


def _coerce(tool_name: str, tool_args: dict) -> dict:
    """Force tool arguments to the types the schema declares.

    The 2B model emits {"title": null} and omits required string args, which made
    tools die with 'NoneType' object has no attribute 'strip' — that failure string
    was then fed back to the model as its "fact" (events.db rows 242/245,
    records/2026-11-08-20-44-17.md). Coercing to ""/0 keeps the tool running and
    keeps the hallucination channel shut.
    """
    props = _SCHEMA_PARAMS.get(tool_name, {})
    out = dict(tool_args) if isinstance(tool_args, dict) else {}
    for key, spec in props.items():
        t = spec.get("type")
        v = out.get(key)
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
        return f"Unknown tool: {tool_name}"
    try:
        return str(fn(_coerce(tool_name, tool_args)))
    except Exception as e:
        return f"Tool '{tool_name}' failed: {e}"
