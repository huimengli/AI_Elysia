"""Vision tower tool: full-screen capture answered by the multimodal model.

OCR (`read_screen` / `find_on_screen`) reads characters; it is unreliable for
Chinese (WinRT OCR inserts spaces between glyphs and misreads them: measured
2026-11-16 15:20 `稻 杳 一 哔 哩 哔 哩 bilibili`) and cannot tell which thumbnail
is the first video. This tool asks the vision model, which sees layout, icons and
covers. The two are complementary, so OCR stays in place.
"""
import base64
import io
import re
import time
from pathlib import Path

import pyautogui

pyautogui.FAILSAFE = False

_PROMPT = (
    "你是屏幕助手，这是一张整屏截图（像素坐标与屏幕坐标一致）。"
    "问题：{q}。"
    "要求：只回答一行，格式是 (x,y) 它是什么，x y 是它中心的整数像素坐标；"
    "找不到就只回答「找不到」。不要输出 JSON、代码块或其他格式，不要编造坐标。"
)


def _coords(ans: str) -> tuple[int, int] | None:
    """First two integers in the answer are the coordinates.

    The model returns formats that vary ( (127,396) , ["center","0","127","396"] ),
    so take the first integer pair rather than matching one shape.
    """
    nums = re.findall(r"\d+", ans)
    if len(nums) >= 2:
        x, y = int(nums[0]), int(nums[1])
        if 0 <= x <= 4000 and 0 <= y <= 4000:
            return x, y
    return None


def describe_screen(question: str) -> str:
    """Capture the whole screen and ask the vision tower about it.

    Evidence discipline: the answer is the model's own words. If the capture
    fails or the tower does not answer, the tool says so — no invented answer.
    """
    try:
        img = pyautogui.screenshot()
    except Exception as e:
        return f"截图失败（{type(e).__name__}: {e}），看不到屏幕。"

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png = buf.getvalue()

    # Traceable artifact, same convention as screenshot() (.tmp/screens)
    out_dir = Path(__file__).parent.parent.parent / ".tmp" / "screens"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f"describe_{int(time.time())}.png"
    path.write_bytes(png)

    from jarvis.llm import chat_image
    ans = chat_image(_PROMPT.format(q=question), png).strip()
    if ans.startswith("[LLM"):
        return (f"视觉塔没有回答：{ans}"
                f"（截图已存 {path}；请确认 llama 带 --mmproj 启动）")
    c = _coords(ans)
    if c:
        return (f"视觉回答：{ans}（点击坐标 x={c[0]} y={c[1]}，配 点击坐标用；"
                f"截图 {path.name}，{len(png)} 字节）")
    return f"视觉回答：{ans}（没有给出坐标；截图 {path.name}，{len(png)} 字节）"
