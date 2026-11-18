import html
import json
import re
import urllib.parse
import urllib.request


def search(query: str, max_results: int = 5) -> str:
    """搜索 = **打开浏览器搜索页**（2026-11-18 10:17 第 2d 项：「搜索改为 -> 打开浏览器,
    引擎选择baidu,bing兜底」）。baidu 首选；baidu 被反爬挡住/落不到搜索页时用 bing 兜底。

    判据是 CDP 复读的**页面地址与标题**（我起的窗口，profile 认 pid 口径），不看页面外观；
    两个引擎都不行就如实报，绝不谎称「搜到了」。结果文本不在这一步给：要看结果请用
    `read_screen` / `find_on_screen`（浏览器窗口是我起的，能读）。
    """
    from jarvis.tools.app_control import open_url
    from jarvis.tools.browser_cdp import PAGE_JS, evaluate

    q = urllib.parse.quote(query, safe="")
    engines = [("baidu", f"https://www.baidu.com/s?wd={q}"),
               ("bing", f"https://www.bing.com/search?q={q}")]
    log = []
    for name, url in engines:
        log.append(open_url(url))
        s, e = evaluate(PAGE_JS)
        if not s:
            log.append(f"CDP 连不上，无法复读页面（{e}）")
            continue
        d = json.loads(s)
        addr, title = str(d.get("地址", "")), str(d.get("标题", ""))
        log.append(f"页面证据：标题「{title}」地址 {addr}")
        if name == "baidu" and "baidu.com/s?" in addr:
            return (f"搜索「{query}」已用 baidu 打开浏览器：{url}\n" + "\n".join(log) +
                    "\n要看结果请用 `read_page`（我起窗口的 DOM 中文读得到）；"
                    "这台机器没有中文 OCR，`read_screen`/`find_on_screen` 对中文必然找不到。")
        log.append(f"baidu 落不到搜索页（标题「{title}」），换 bing 兜底")
    return (f"搜索「{query}」两个引擎都没有落到搜索页，**没有搜到**。\n" + "\n".join(log))


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
        # 2026-11-17 19:25 fix (`tests/2026-11-17-18-46-00_cc/record_1.md` 轮 1):
        # `urllib.request` 对含中文的 URL 直接报 `'ascii' codec can't encode characters`
        # （jarvis 传 `https://search.bilibili.com/all?keyword=月声尽,心灯明` 时连撞 1 次）。
        # 路径段按 `quote(safe="/")`、查询串按 `quote(safe="=&/%")` 先编码再请求。
        parts = urllib.parse.urlsplit(url)
        path = urllib.parse.quote(parts.path, safe="/%")
        query = urllib.parse.quote(parts.query, safe="=&%")
        url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))
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
