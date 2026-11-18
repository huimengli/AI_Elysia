"""CDP client for the Chrome instance jarvis launches itself.

Purpose (records/2026-11-17-14-08-00.md): driving the Bilibili player through the DOM,
because three measured facts killed the cheaper routes —
- the `m` keyboard shortcut did **not** close the danmaku (shots 14-03-13 / 14-04-18);
- the control bar shows only on hover and auto-hides in 2-3 s (a cropped strip came back
  all black, 1058 bytes), so a time reading cannot be captured after the fact;
- coordinate clicks in the player/sidebar switched the video.

Measured semantics, all by CDP, not guessed (records/2026-11-17-14-08-00.md):
- danmaku switch: the real control is `INPUT.bui-danmaku-switch-input` inside
  `.bpx-player-dm-switch`; `checked=true` + class `state-1` = 显示,
  `checked=false` + `state-3` = 关闭 (verified by two toggling real clicks);
- lowest quality: `li.bpx-player-ctrl-quality-menu-item` with text 「360P 流畅」; after it
  applies, `video.videoWidth x videoHeight` = 640x360 (the switch lags a few seconds);
- autoplay: `input[aria-label="自动开播"]` can be set to unchecked, **but playback still
  advanced to the next video at the end** (t+10 s in the 14:30 test), so closing the window
  at the end is the step that actually prevents连播;
- synthetic `dispatchEvent` is ignored by the player: clicks must go through
  `Input.dispatchMouseEvent` (trusted events), at coordinates taken from
  `getBoundingClientRect()` — page coordinates, not vision coordinates.

Scope: port 9333 is passed only when jarvis launches its own Chrome with its own
`.tmp/chrome_profile`, listening on 127.0.0.1. The user's windows and profile are never
touched. No new dependency: `.venv` already ships `websockets`.
"""

import json
import subprocess
import time
import urllib.request

CDP_PORT = 9333

STATE_JS = """(() => {
  const v=document.querySelector('video');
  const dm=document.querySelector('.bui-danmaku-switch-input');
  const ap=document.querySelector('input[aria-label="自动开播"]');
  return JSON.stringify({标题: document.title.slice(0,40), 地址: location.href.slice(0,46),
    ct: v && Number(v.currentTime.toFixed(1)), du: v && v.duration,
    paused: v && v.paused, ended: v && v.ended,
    分辨率: v && (v.videoWidth+'x'+v.videoHeight),
    弹幕checked: dm && dm.checked, autoplay: ap && ap.checked});
})()"""

READY_JS = """(() => {
  const v=document.querySelector('video');
  return JSON.stringify({有video:!!v, du:v&&v.duration, ct:v&&Number(v.currentTime.toFixed(1)),
    菜单项数:document.querySelectorAll('li.bpx-player-ctrl-quality-menu-item').length,
    弹幕input:!!document.querySelector('.bui-danmaku-switch-input'),
    标题:document.title.slice(0,30)});
})()"""

# Round 4 (record_15.md): setup ran while the page was still loading — `菜单项:[]` and every
# field null, so `video` did not exist and no play was ever issued. Readiness must be checked
# first: a real `video` element with a duration.
# Round 6 (record_16.md): the danmaku input and the quality menu are **absent from the DOM**
# while the control bar is hidden, so setup ran and silently did nothing (`菜单项:[]`, no
# `danmakuChecked`); Bilibili also resumed at the last watched position (ct=209 of 223), so
# playback is sent back to 0 — 只听歌 means the whole song.
SETUP_JS = """(() => {
  const out={};
  const dm=document.querySelector('.bui-danmaku-switch-input');
  if(dm){ if(dm.checked) dm.click(); out.danmakuChecked=dm.checked; }
  const ap=document.querySelector('input[aria-label="自动开播"]');
  if(ap){ if(ap.checked) ap.click(); out.autoplay=ap.checked; }
  const items=[...document.querySelectorAll('li.bpx-player-ctrl-quality-menu-item')];
  const t=items.find(x=>x.textContent.trim().replace(/\\s+/g,' ')==='360P 流畅');
  if(t){ t.click(); out.点过最低档=true; }
  const v=document.querySelector('video');
  if(v){ if(v.currentTime>1){ v.currentTime=0; out.回到0点=true; }
         if(v.paused){ v.play(); out.已发起播放=true; } else { out.已在播放=true; } }
  out.菜单项=items.map(x=>x.textContent.trim().replace(/\\s+/g,' '));
  return JSON.stringify(out);
})()"""

# Control-bar aria-labels, read for evidence when a trusted play click is needed.
PLAY_RECT_JS = """(() => {
  const bs=[...document.querySelectorAll('[aria-label]')].filter(e=>/播放/.test(e.getAttribute('aria-label')));
  const one=bs.find(e=>e.getAttribute('aria-label')==='播放/暂停') || bs[0];
  if(!one) return 'NF';
  const r=one.getBoundingClientRect();
  return JSON.stringify({label:one.getAttribute('aria-label'), x:r.x+r.width/2, y:r.y+r.height/2,
    候选:bs.map(e=>e.getAttribute('aria-label'))});
})()"""


def targets(port: int = CDP_PORT) -> list[dict]:
    """Page targets Chrome reports. [] when the port is not open (no window of mine was
    launched with --remote-debugging-port)."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=3) as r:
            return json.load(r)
    except Exception:
        return []


def _pick(ts: list[dict], kw: str) -> dict | None:
    """Pick a page target by a substring of title/url. Empty kw = the first page, which is
    my own window (the title changes as videos switch, so a title is not a stable key)."""
    for t in ts:
        if t.get("type") == "page" and (not kw or kw in (t.get("title", "") + t.get("url", ""))):
            return t
    return None


class CDP:
    """One page connection: evaluate JS, read rects, trusted click."""

    def __init__(self, ws_url: str):
        from websockets.sync.client import connect
        self.ws = connect(ws_url, max_size=16 * 1024 * 1024)
        self.i = 0

    def send(self, method: str, params: dict | None = None) -> dict:
        self.i += 1
        mid = self.i
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mid:
                return {"__error": m["error"]} if "error" in m else m.get("result", {})

    def ev(self, expr: str) -> tuple[str, str]:
        r = self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        if "__error" in r:
            return ("", str(r["__error"]))
        res = r.get("result", {})
        v = res.get("value") if res.get("type") == "string" else json.dumps(
            res.get("value"), ensure_ascii=False)
        return (v, "")

    def rect(self, sel: str, text: str = "") -> tuple[float, float] | None:
        """Centre of the element matching `sel` (optionally whose text equals `text`), in
        page CSS px. None when nothing matches — reported, never guessed."""
        js = """(() => {
          let els=[...document.querySelectorAll('%s')];
          if('%s') els=els.filter(e=>e.textContent.trim().replace(/\\s+/g,' ')==='%s');
          if(!els.length) return 'NF';
          const r=els[0].getBoundingClientRect();
          return JSON.stringify({x:r.x+r.width/2, y:r.y+r.height/2});
        })()""" % (sel, text, text)
        v, e = self.ev(js)
        if e or v == "NF":
            return None
        p = json.loads(v)
        return (p["x"], p["y"])

    def hover(self, x: float, y: float) -> None:
        """Move the pointer inside the page (page CSS px). Bilibili's control bar appears on
        hover, and the danmaku input plus the quality menu only exist in the DOM while it is
        shown (round 6), so hovering is a real prerequisite, not a cosmetic step."""
        self.send("Input.dispatchMouseEvent",
                  {"type": "mouseMoved", "x": x, "y": y, "button": "none"})

    def real_click(self, x: float, y: float) -> None:
        """Trusted mouse events at page coordinates. The move first makes the control bar
        appear (it auto-hides in 2-3 s), then press/release."""
        self.send("Input.dispatchMouseEvent",
                  {"type": "mouseMoved", "x": x, "y": y, "button": "none"})
        time.sleep(0.25)
        self.send("Input.dispatchMouseEvent",
                  {"type": "mousePressed", "x": x, "y": y, "button": "left",
                   "clickCount": 1, "buttons": 1})
        time.sleep(0.08)
        self.send("Input.dispatchMouseEvent",
                  {"type": "mouseReleased", "x": x, "y": y, "button": "left",
                   "clickCount": 1, "buttons": 0})

    def close(self) -> None:
        self.ws.close()


def open_cdp(kw: str = "", port: int = CDP_PORT) -> tuple[CDP | None, str]:
    """Connect to one of jarvis' pages. Returns (client, "") or (None, honest reason)."""
    ts = targets(port)
    if not ts:
        return (None, f"CDP 端口 {port} 连不上（没有我起的窗口带 --remote-debugging-port）")
    t = _pick(ts, kw)
    if t is None:
        return (None, f"我的页面里找不到标题/地址含「{kw}」的目标（现有 "
                      f"{[x.get('title', '')[:30] for x in ts if x.get('type') == 'page']}）")
    try:
        return (CDP(t["webSocketDebuggerUrl"]), "")
    except Exception as e:
        return (None, f"连 CDP websocket 失败：{e}")


def navigate(url: str, kw: str = "", port: int = CDP_PORT) -> tuple[str, str]:
    """CDP `Page.navigate` on one of jarvis' pages. Returns (address evidence, "").

    Keyboard route (Ctrl+L + type + Enter) proved fragile in the field
    (round 4, 10:55, tests/2026-11-18-10-17-23_cc/record_4.md): the same Chrome
    instance had its own 「要恢复页面吗？」/「无法更新 Chrome」 dialogs, so the keystrokes
    landed on a dialog and the address bar never moved (12 s, address stayed baidu).
    `Page.navigate` needs no focus, no keyboard, no vision, no click.
    """
    c, e = open_cdp(kw, port)
    if c is None:
        return ("", e)
    try:
        r = c.send("Page.navigate", {"url": url})
        err = (r or {}).get("error")
        if err:
            return ("", f"Page.navigate 被页面拒绝：{err}")
        v, e2 = c.ev(PAGE_JS)
        return (v, e2)
    finally:
        c.close()


def evaluate(expr: str, kw: str = "", port: int = CDP_PORT) -> tuple[str, str]:
    c, e = open_cdp(kw, port)
    if c is None:
        return ("", e)
    try:
        return c.ev(expr)
    finally:
        c.close()


def pages(port: int = CDP_PORT) -> list[tuple[str, str]]:
    """我起实例里**所有**标签页的 (标题, 地址)。

    2026-11-18 10:30 自曝：`open_cdp("")` 只取**第一个** page target，多标签时读到的
    不是活动标签 —— `open_site('github')` 的复读一直是 `https://www.baidu.com/`（b站导航
    同理）。所以验证导航必须看全部标签，不能只读第一个。
    """
    import json

    out = []
    for t in targets(port):
        if t.get("type") != "page":
            continue
        try:
            c = CDP(t["webSocketDebuggerUrl"])
            try:
                v, e = c.ev(PAGE_JS)
                if v:
                    d = json.loads(v)
                    out.append((str(d.get("标题", "")), str(d.get("地址", ""))))
            finally:
                c.close()
        except Exception:
            continue
    return out


def kill_recorded_pid(pid: int) -> str:
    """Close a window by killing a pid jarvis recorded for itself (need_user Q29/Q32/Q34).
    Pids jarvis never recorded are refused."""
    from jarvis.tools.app_control import forget_pid, jarvis_pids
    if pid not in jarvis_pids():
        return f"pid {pid} 不在我起的窗口记录里，拒绝关闭。"
    # **只杀这一个 pid，不杀进程树**（11:12 自曝，record_6.md 轮 6b：`taskkill /T` 把
    # Weixin 10788 当成 chrome pid 2736 的子进程一起杀了 —— 那是你早上开的微信，
    # 不在我的窗口记录里）。渲染子进程会在浏览器主进程退出后自行收尾。
    r = subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                       capture_output=True, text=True)
    out = r.stdout.strip() or r.stderr.strip()
    if r.returncode == 0:
        # The pid is gone; keep the record honest so the kill permission never
        # points at a dead pid (21:47 self-disclosure in records/2026-11-17-20-16-55.md).
        forget_pid(pid)
    return out


# --- 唤醒 ducking（records/2026-11-18-10-17-23.md 第 1 项）---

PAUSE_JS = """(() => {
  const v=document.querySelector('video');
  if(!v) return JSON.stringify({有video:false});
  const was=!v.paused && !v.ended;
  v.pause();
  return JSON.stringify({有video:true, 播放中:was, paused:v.paused,
    ct:Number(v.currentTime.toFixed(1)), du:v.duration});
})()"""

RESUME_JS = """(() => {
  const v=document.querySelector('video');
  if(!v) return JSON.stringify({有video:false});
  v.play();
  return JSON.stringify({有video:true, paused:v.paused,
    ct:Number(v.currentTime.toFixed(1)), du:v.duration});
})()"""

PAGE_JS = """(() => JSON.stringify({标题:document.title.slice(0,60),地址:location.href.slice(0,90)}))()"""

# Only a pause **we** issued is resumed, so a video the user paused by hand stays paused
# (22:05 music uniqueness + 10:17 ducking: never act on windows we did not start).
_duck_state = {"paused": False}


def duck(action: str = "pause", explicit: bool = False) -> str:
    """唤醒触发时暂停我自己起窗口里的播放，回复（TTS）播报完成后恢复。

    只碰我自己起的窗口：CDP 端口 9333 只在我起的实例上监听，`open_cdp` 连不上就是
    「没有我起的窗口」，此时如实返回，绝不猜「已暂停」。恢复只针对**我暂停过的**播放，
    你手动暂停的视频不会被我说「恢复」掉。回读 `paused` 为证，不看页面外观。
    """
    import json

    if action == "pause":
        s, e = evaluate(PAUSE_JS)
        if not s:
            return f"没有暂停任何播放（CDP 连不上：{e}）"
        d = json.loads(s)
        if not d.get("有video"):
            return "没有暂停任何播放（我自己起的窗口里没有 video 元素）"
        if d.get("播放中"):
            _duck_state["paused"] = True
            return (f"已暂停我自己的播放（回读 paused={d.get('paused')}，"
                    f"ct={d.get('ct')}/{d.get('du')}）")
        return f"没有在播，无需暂停（回读 paused={d.get('paused')}，ct={d.get('ct')}）"

    if not _duck_state["paused"] and not explicit:
        return "没有我暂停过的播放，无需恢复。"
    s, e = evaluate(RESUME_JS)
    if not s:
        return f"恢复失败（CDP 连不上：{e}）"
    d = json.loads(s)
    was_mine = _duck_state["paused"]
    _duck_state["paused"] = False
    who = "我按的暂停" if was_mine else "不是按的暂停（媒体键/你手动）"
    return (f"已恢复播放（回读 paused={d.get('paused')}，"
            f"ct={d.get('ct')}/{d.get('du')}；暂停来源：{who}，按用户指令恢复）"
            if explicit else
            f"已恢复播放（回读 paused={d.get('paused')}，ct={d.get('ct')}/{d.get('du')}）")


# ─── 我起窗口的页面读取（2026-11-18 12:30，P1 中文「OCR」替代路线） ───
# 本机没有可用中文 OCR：`Windows.Media.Ocr` 在这台机器不可用（wow-sight selftest 早测过），
# Umi-OCR 只有 Downloads 里的自解压安装包、没有安装、:50015 无监听（12:25 实测连接被拒）。
# 所以对**我自己起的浏览器窗口**，文本一律走 CDP 读 DOM（无 OCR、无视觉、无坐标猜测）；
# 桌面（非我起窗口）的中文识别仍是 P1，挂 Q37 等你决定是否常驻 Umi-OCR。

PAGE_TEXT_JS = """(() => JSON.stringify({标题:document.title.slice(0,60),
  地址:location.href.slice(0,90),
  正文:document.body.innerText.slice(0,1200)}))()"""


def read_page(kw: str = "", port: int = CDP_PORT) -> str:
    """读我自己起的浏览器窗口的可见文本（innerText），带标题+地址复读。"""
    s, e = evaluate(PAGE_TEXT_JS, kw, port)
    if not s:
        return f"读不到页面文本（CDP 连不上：{e}）"
    d = json.loads(s)
    return (f"我起的浏览器窗口 标题「{d['标题']}」 地址 {d['地址']}\n"
            f"页面正文（innerText 前 1200 字）：\n{d['正文']}")


def _find_js(text: str) -> str:
    t = json.dumps(text, ensure_ascii=False)
    return ("(() => { const t=" + t + "; const sel='a,button,[role=button],h1,h2,h3,h4,li';"
           " const hits=[]; for(const el of document.querySelectorAll(sel)){"
           " const s=(el.innerText||'').trim(); if(!s) continue;"
           " if(s.includes(t) || t.includes(s)){"
           " const r=el.getBoundingClientRect(); if(r.width<1||r.height<1) continue;"
           " hits.push({文本:s.slice(0,40), x:Math.round(r.x+r.width/2),"
           " y:Math.round(r.y+r.height/2), href:(el.href||'').slice(0,70)});"
           " if(hits.length>=5) break; } }"
           " const cand=[]; for(const el of document.querySelectorAll(sel))"
           "{const s=(el.innerText||'').trim(); if(s){cand.push(s.slice(0,30));"
           " if(cand.length>=10) break;}}"
           " return JSON.stringify({命中:hits, 候选:cand}); })()")


def find_page_text(text: str, click: bool = False, kw: str = "",
                   port: int = CDP_PORT) -> str:
    """在我起的窗口里按 DOM 文本找元素；click=True 时用 CDP 受信点击点它，点击后复读标题/地址。
    坐标是页面 CSS px（`getBoundingClientRect`），不是视觉坐标。"""
    c, e = open_cdp(kw, port)
    if c is None:
        return f"读不到页面（CDP 连不上：{e}）"
    try:
        v, e2 = c.ev(_find_js(text))
        if not v:
            return f"页面查找失败：{e2}"
        d = json.loads(v)
        if not isinstance(d, dict):
            return f"页面查找没有拿到结构化结果（JS 返回 {str(d)[:40]}），如实报告，不猜。"
        hits = d.get("命中") or []
        if not hits:
            return (f"页面里找不到「{text}」（我起的窗口，DOM 文本匹配，没有 OCR）。"
                    f"页面上能看到的条目：{d.get('候选')}")
        if not click:
            return (f"找到 {len(hits)} 处「{text}」："
                    f"{[(h['文本'], h['x'], h['y']) for h in hits[:3]]}（页面坐标，可点）")
        h = hits[0]
        c.real_click(h["x"], h["y"])
        time.sleep(1.0)
        v2, e3 = c.ev(PAGE_JS)
        d2 = json.loads(v2) if v2 else {}
        return (f"已用 CDP 受信点击「{h['文本']}」 @(x={h['x']},y={h['y']})"
                f"（页面坐标，非视觉坐标），点击后复读 标题「{d2.get('标题')}」"
                f" 地址 {d2.get('地址')} {e3}")
    finally:
        c.close()
