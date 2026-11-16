"""Vision tower tool: full-screen capture answered by the multimodal model.

OCR (`read_screen` / `find_on_screen`) reads characters; it is unreliable for
Chinese (WinRT OCR inserts spaces between glyphs and misreads them: measured
2026-11-16 15:20 `稻 杳 一 哔 哩 哔 哩 bilibili`) and cannot tell which thumbnail
is the first video. This tool asks the vision model, which sees layout, icons and
covers. The two are complementary, so OCR stays in place.
"""
import base64
import io
import time
from pathlib import Path

import pyautogui

pyautogui.FAILSAFE = False

_PROMPT = (
    "你是屏幕助手，这是一张整屏截图（像素坐标与屏幕坐标一致）。"
    "问题：{q}。"
    "要求：若问题要找可点击的东西，回答它中心的整数像素坐标（x,y）和它是什么；"
    "找不到就只回答「找不到」。不要编造坐标。"
)


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
    return f"视觉回答：{ans}（截图 {path.name}，{len(png)} 字节，坐标可配 点击坐标）"
