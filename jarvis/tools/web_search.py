import html
import json
import re
import urllib.parse
import urllib.request

from ddgs import DDGS


def search(query: str, max_results: int = 5) -> str:
    """Search the web via DuckDuckGo and return a formatted text summary."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "没有找到结果。"
        return "\n".join(f"- {r['title']}: {r['body']}" for r in results)
    except Exception as e:
        return f"搜索失败：{e}"


def get_weather(location: str = "") -> str:
    """Get current weather using wttr.in (no API key needed).

    HB-035（2026-11-13）：中文地名以前直接拼进 URL，`urllib` 在 ascii 编码阶段就崩
    （`'ascii' codec can't encode characters`，12:12:23 连 3 次）。现在路径段按
    `quote(..., safe="")` 编码，并且改用 `format=j1`（纯 ASCII 的 JSON），中文文案
    在 Python 侧拼装，URL 里不再出现任何非 ASCII 字节。
    """
    try:
        loc = urllib.parse.quote(location.strip(), safe="") if location.strip() else ""
        url = f"https://wttr.in/{loc}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        cur = data["current_condition"][0]
        area = (data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value")
                or location.strip() or "本地")
        desc = cur.get("weatherDesc", [{}])[0].get("value", "")
        return (f"{area}：{desc}，气温 {cur.get('temp_C')}°C，"
                f"湿度 {cur.get('humidity')}%，风速 {cur.get('windspeedKmph')} km/h")
    except Exception as e:
        return f"天气查询失败：{e}"


def fetch_page(url: str, max_chars: int = 3000) -> str:
    """Fetch a URL and return its plain text content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
        raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL)
        raw = re.sub(r"<[^>]+>", " ", raw)
        raw = html.unescape(raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw[:max_chars]
    except Exception as e:
        return f"读取网页失败 {url}：{e}"
