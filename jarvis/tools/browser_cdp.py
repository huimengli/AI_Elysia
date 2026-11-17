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


def evaluate(expr: str, kw: str = "", port: int = CDP_PORT) -> tuple[str, str]:
    c, e = open_cdp(kw, port)
    if c is None:
        return ("", e)
    try:
        return c.ev(expr)
    finally:
        c.close()


def kill_recorded_pid(pid: int) -> str:
    """Close a window by killing a pid jarvis recorded for itself (need_user Q29/Q32/Q34).
    Pids jarvis never recorded are refused."""
    from jarvis.tools.app_control import forget_pid, jarvis_pids
    if pid not in jarvis_pids():
        return f"pid {pid} 不在我起的窗口记录里，拒绝关闭。"
    r = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       capture_output=True, text=True)
    out = r.stdout.strip() or r.stderr.strip()
    if r.returncode == 0:
        # The pid is gone; keep the record honest so the kill permission never
        # points at a dead pid (21:47 self-disclosure in records/2026-11-17-20-16-55.md).
        forget_pid(pid)
    return out
