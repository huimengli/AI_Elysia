"""Jarvis Web UI — runs alongside voice as a background thread."""
from __future__ import annotations
import asyncio
import json
from fastapi import Response  # 第 181 处自曝后照实补：页面禁缓存（jarvis 起的窗口被 Chrome 启发式缓存喂旧版，第 1/4/5/6 条的前端改动进不去）
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from starlette.websockets import WebSocketDisconnected
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from jarvis.tts import speak_streamed, stop_speaking, is_speaking
from jarvis import services as svc

_STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Jarvis")
# 顶栏三页共用一份（design v3.2 §3-5）：`/static/tabs.css` + `/static/tabs.js`。
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
_clients: list[WebSocket] = []
_loop: asyncio.AbstractEventLoop | None = None


# ─── Capture the REAL event loop at startup ───

@app.on_event("startup")
async def _capture_loop():
    global _loop
    _loop = asyncio.get_running_loop()
    svc.jlog("[Web] Event loop captured — WebSocket broadcast ready.")  # 第 2 条：不往控制台刷
    asyncio.create_task(_monitor_loop())


# ─── Thread-safe broadcast ───

def _broadcast_to_ws(event: dict) -> None:
    """Send event to all connected WebSocket clients.
    Thread-safe — can be called from voice/keyboard threads."""
    if not _loop or _loop.is_closed():
        return
    try:
        asyncio.run_coroutine_threadsafe(_async_broadcast(event), _loop)
    except RuntimeError:
        pass  # loop closed during shutdown


async def _async_broadcast(event: dict) -> None:
    """Actually send the event — runs on the event loop thread."""
    data = json.dumps(event)
    for ws in list(_clients):
        try:
            await ws.send_text(data)
        except Exception as e2:
            if ws in _clients:
                _clients.remove(ws)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse((_STATIC_DIR / "index.html").read_text(encoding="utf-8"), headers=_NO_STORE)


@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    """浏览器每次访问页面都会自动取 `/favicon.ico`；缺文件时控制台永远有一条 404
    （实测 `tests/2026-11-12-23-08-35_cc/record_2.md`）。图标是主题色（粉 + 丁香 + 金）
    的小圆盘，16/32/48/64 四档尺寸，放在 `jarvis/static/`（与 `index.html` 同一约定）。
    """
    p = _STATIC_DIR / "favicon.ico"
    if not p.is_file():
        return Response(status_code=204)  # 宁可不给图标，也不要抛 500
    return FileResponse(p, media_type="image/x-icon")


# ─── Provider APIs ───

@app.get("/api/providers")
async def api_providers():
    from jarvis.main import get_providers, get_active_provider
    providers = get_providers()
    active = get_active_provider()
    result = {}
    for key, prov in providers.items():
        result[key] = {
            "label": prov.get("label", key),
            "model": prov.get("model", ""),
            "type": prov.get("type", "ollama"),
            "base_url": prov.get("base_url", ""),
            "api_key": prov.get("api_key", ""),
        }
    return JSONResponse({"providers": result, "active": active})


@app.post("/api/providers/{provider_key}")
async def api_set_provider(provider_key: str):
    from jarvis.main import set_active_provider
    ok = set_active_provider(provider_key)
    if ok:
        return JSONResponse({"status": "ok", "active": provider_key})
    return JSONResponse({"status": "error", "message": "Unknown provider"}, status_code=400)


@app.put("/api/providers/{provider_key}")
async def api_upsert_provider(provider_key: str, request: Request):
    """Add or update a provider."""
    from jarvis.main import _load_config, _save_config
    body = await request.json()
    cfg = _load_config()
    providers = cfg.setdefault("llm", {}).setdefault("providers", {})
    providers[provider_key] = {
        "type": body.get("type", "openai"),
        "label": body.get("label", provider_key),
        "model": body.get("model", ""),
        "base_url": body.get("base_url", ""),
    }
    if body.get("api_key"):
        providers[provider_key]["api_key"] = body["api_key"]
    _save_config(cfg)
    return JSONResponse({"status": "ok", "provider": provider_key})


@app.delete("/api/providers/{provider_key}")
async def api_delete_provider(provider_key: str):
    """Delete a provider."""
    from jarvis.main import _load_config, _save_config, get_active_provider
    cfg = _load_config()
    providers = cfg.get("llm", {}).get("providers", {})
    if provider_key not in providers:
        return JSONResponse({"status": "error", "message": "Not found"}, status_code=404)
    if provider_key == get_active_provider():
        return JSONResponse({"status": "error", "message": "Cannot delete active provider"}, status_code=400)
    del providers[provider_key]
    _save_config(cfg)
    return JSONResponse({"status": "ok"})


# ─── Settings APIs ───

@app.get("/api/settings")
async def api_get_settings():
    """Return all configurable settings."""
    from jarvis.main import _load_config
    cfg = _load_config()
    wake = cfg.get("wake_word", {})
    # Selectable wake models (records/2026-11-13-00-12-17.md 第 4 项): only the
    # options declared in config.yaml (the ones tracked in Git), each with the
    # threshold that was verified for it in ai_buckup/onnx_opinion.md.
    options = [
        {
            "label": o.get("label", Path(o.get("model", "")).stem),
            "model": o.get("model", ""),
            "threshold": o.get("threshold"),
            "current": o.get("model") == wake.get("model"),
        }
        for o in wake.get("model_options", [])
    ]
    return JSONResponse({
        "tts": cfg.get("tts", {}),
        "stt": cfg.get("stt", {}),
        "wake_word": wake,
        "wake_model_options": options,
        "context": cfg.get("context", {}),
        "llm": {
            "temperature": cfg.get("llm", {}).get("temperature", 0.7),
            "active_provider": cfg.get("llm", {}).get("active_provider", "ollama"),
        },
        "tools": cfg.get("tools", {}),
    })


@app.put("/api/settings")
async def api_update_settings(request: Request):
    """Update settings. Accepts partial updates."""
    from jarvis.main import _load_config, _save_config
    body = await request.json()
    cfg = _load_config()

    if "tts" in body:
        cfg.setdefault("tts", {}).update(body["tts"])
    if "stt" in body:
        cfg.setdefault("stt", {}).update(body["stt"])
    wake_changed = "wake_word" in body
    if wake_changed:
        cfg.setdefault("wake_word", {}).update(body["wake_word"])
    if "context" in body:
        cfg.setdefault("context", {}).update(body["context"])
    if "llm" in body:
        if "temperature" in body["llm"]:
            cfg.setdefault("llm", {})["temperature"] = body["llm"]["temperature"]
    if "tools" in body:
        cfg.setdefault("tools", {}).update(body["tools"])

    _save_config(cfg)
    if wake_changed:
        # model + threshold were written together; make the listening loop pick
        # them up without a restart (records/2026-11-13-00-12-17.md 第 4 项).
        from jarvis.wake import request_wake_reload
        request_wake_reload()
    return JSONResponse({"status": "ok"})


# ─── Mute APIs ───

@app.get("/api/mute")
async def api_get_mute():
    from jarvis.main import is_muted
    return JSONResponse({"muted": is_muted()})


@app.post("/api/mute")
async def api_toggle_mute():
    from jarvis.main import toggle_mute, is_muted
    toggle_mute()
    return JSONResponse({"muted": is_muted()})


# ─── Event log API (T7) ───

@app.get("/api/events")
async def api_get_events(limit: int = 100):
    """Recent operation records from sqlite — works with or without a live session."""
    from jarvis.main import event_log
    return JSONResponse({"events": event_log.recent(min(max(limit, 1), 500))})

# ─── Health API (2026-11-09-15-37-58: 顶部状态显示器右侧的三盏灯) ───

def _split_hostport(url: str) -> tuple[str, int]:
    from urllib.parse import urlparse
    p = urlparse(url)
    port = p.port
    if port is None:
        port = 443 if p.scheme == "https" else 80
    return (p.hostname or "", int(port))


_probe_cache: dict = {}


def _tcp_probe(host: str, port: int, timeout: float = 0.8) -> bool:
    """True when something is listening on host:port (loopback probes are cheap)."""
    if not host or port <= 0:
        return False
    key = (host, port)
    hit = _probe_cache.get(key)
    # 节拍实测 1.8 s/拍（第 120 处自曝后量得），掉线探针每次要等 0.8 s；同一秒内共用一次结果。
    if hit and time.time() - hit[0] < 1.0:
        return hit[1]
    import socket
    # 第 121 处自曝：原先在 try 里直返 True/False，TTL 缓存写不进去（缓存形同虚设）。
    ok = False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            ok = True
    except Exception:
        ok = False
    _probe_cache[key] = (time.time(), ok)
    return ok


def _health_snapshot() -> dict:
    """Resolve the four lamps: wake / asr / llm / tts.

    wake and asr live *inside this process*: openWakeWord publishes its live
    state into ``jarvis.wake.state`` (model loaded, mic listening, latest score
    / peak / last trigger), and faster-whisper is loaded lazily by jarvis.stt
    on the first transcription, so "online" means the jarvis process is
    answering (which it is, by definition) and "warm" says whether the whisper
    model is already resident. llm (:8080 llama.cpp) and tts (:9880 GPT-SoVITS)
    are out-of-process servers, so they get a TCP probe against the
    base_url / api_url declared in config.yaml.
    """
    from jarvis.main import _load_config
    import jarvis.stt as stt_mod
    import jarvis.wake as wake_mod

    cfg = _load_config()
    w = getattr(wake_mod, "state", {}) or {}
    last = w.get("last_detect", 0.0) or 0.0
    wake = {
        "online": bool(w.get("online", False)),
        "listening": bool(w.get("listening", False)),
        "model": w.get("model", ""),
        "threshold": w.get("threshold"),
        "score": round(float(w.get("score", 0.0)), 3),
        "peak": round(float(w.get("peak", 0.0)), 3),
        "last_detect": (time.strftime("%H:%M:%S", time.localtime(last)) if last else ""),
        "detail": (
            f"{w.get('model', '')} / threshold {w.get('threshold')} / "
            f"peak {round(float(w.get('peak', 0.0)), 3)}"
            + (f" / 上次触发 {time.strftime('%H:%M:%S', time.localtime(last))}" if last else "")
        ),
    }

    llm_cfg = cfg.get("llm", {})
    active = llm_cfg.get("active_provider", "ollama")
    prov = (llm_cfg.get("providers") or {}).get(active, {})
    base_url = prov.get("base_url", "")
    host, port = _split_hostport(base_url)
    llm = {
        "online": _tcp_probe(host, port),
        "provider": active,
        "label": prov.get("label", active),
        "url": base_url,
        "detail": f"{prov.get('label', active)} @ {base_url}",
    }

    tts_cfg = cfg.get("tts", {})
    tts_provider = tts_cfg.get("provider", "kokoro")
    if tts_provider == "gptsovits":
        tts_url = (tts_cfg.get("gptsovits") or {}).get("api_url", "")
        th, tp = _split_hostport(tts_url)
        online = _tcp_probe(th, tp)
        detail = f"GPT-SoVITS @ {tts_url}"
    else:
        # In-process TTS (kokoro): the jarvis process serves it.
        tts_url = ""
        online = True
        detail = f"本地进程内 ({tts_provider})"
    tts = {"online": online, "provider": tts_provider, "url": tts_url, "detail": detail}

    stt_cfg = cfg.get("stt", {})
    loaded = getattr(stt_mod, "_model", None) is not None
    device = getattr(stt_mod, "_model_device", None)
    engine = stt_cfg.get("engine", "whisper")
    asr = {
        "online": True,
        "warm": loaded,
        "engine": engine,
        "model": stt_cfg.get("model", "small"),
        "language": stt_cfg.get("language", "zh"),
        "device": device or stt_cfg.get("device", "cpu"),
        "detail": (
            ("faster-whisper " if engine == "whisper" else "sherpa-onnx Paraformer ")
            + f"{stt_cfg.get('model', 'small')} / "
            f"{device or stt_cfg.get('device', 'cpu')} / "
            f"{stt_cfg.get('language', 'zh')}（模型已加载={loaded}）"
        ),
    }
    return {"wake": wake, "asr": asr, "llm": llm, "tts": tts}


@app.get("/api/health")
async def api_health():
    """Four lamps for the UI: 唤醒 / 语音识别 / LLM / TTS."""
    import asyncio
    return JSONResponse(await asyncio.to_thread(_health_snapshot))


# ─── WebSocket ───


# ─── Monitor（design v3.1 §3/§4/§5，Q30 的 G/F/A/B/C/E 块）───

_mon_state: dict = {}      # ws -> {"interval": int, "cursor": {name: int}}
_mon_interval = 5          # 全局节拍 = 各客户端的最小间隔


@app.get("/about", response_class=FileResponse)
async def about():
    """about（相关页面）：只写已实现的事实，不写没实现过的功能（design v3.2 §3-5）。"""
    return FileResponse(_STATIC_DIR / "about.html", headers=_NO_STORE)



# 第 181 处自曝（照实坐实）：jarvis 起的窗口拿到的是 Chrome 启发式缓存里的旧页 —— `FileResponse`
# 不发缓存头，前端改动（样式/滚动/200 行上限/每拍一次赋值）在真会话里不生效。这里显式 no-store。
_NO_STORE = {"Cache-Control": "no-store, must-revalidated", "Pragma": "no-cache"}

@app.get("/monitor", response_class=FileResponse)
async def monitor_page():
    """独立页 /monitor（Q30-2 选定，1080p 起）。"""
    return FileResponse(_STATIC_DIR / "monitor.html", headers=_NO_STORE)


@app.get("/api/monitor_logs")
async def api_monitor_logs(name: str = "monitor", since: int = 0):
    """只读取证口：把 Monitor 日志环（含推送循环的异常）暴露出来。第 136-137 处自曝后加。"""
    part, new = svc.logs_since(name, since)
    return JSONResponse({"name": name, "lines": part, "cursor": new})


@app.get("/api/monitor")
async def api_monitor():
    snap = await asyncio.to_thread(svc.snapshot)
    # B 块四灯在快照里也要有（轮 1 自曝：只有 WS 推送带，/api/monitor 空）
    snap["lamps"] = await asyncio.to_thread(_health_snapshot)
    snap["clients"] = len(_mon_state)
    # 第 155 处取证：服务端有客户端、无发送失败，页面收不到 —— 把每个客户端的现场摆出来。
    snap["client_info"] = [{"iv": v["interval"], "cur": len(v["cursor"]), "id": id(ws)} for ws, v in _mon_state.items()]
    return JSONResponse(snap)


@app.post("/api/service/stop")
async def api_service_stop(req: Request):
    """关闭按钮只认 jarvis 自起的 pid（design §5）；外部 pid 拒绝并回显 taskkill 真实输出。"""
    body = await req.json()
    name = str(body.get("name", ""));
    pid = int(body.get("pid", 0));
    out = svc.stop_service(name, pid)
    return JSONResponse({"name": name, "pid": pid, "result": out,
                           "refused": out.startswith("拒绝")})


async def _monitor_loop():
    """服务端采样与推送同一节拍（Q30-3：最低 1 s）；日志每轮最多 20 行。"""
    while True:
        try:
            t0 = time.time()
            if not _mon_state:
                # 没有监控客户端时也要 sleep：旧写法 `continue` 空转，白烧 CPU（第 104 处自曝一并修）
                await asyncio.sleep(1)
                continue
            snap = await asyncio.to_thread(svc.snapshot)
            # B 块四灯（唤醒/语音识别/LLM/TTS）复用现成的 /api/health 探针，不新写
            snap["lamps"] = await asyncio.to_thread(_health_snapshot)
            for ws in list(_mon_state.keys()):
                st = _mon_state.get(ws)
                if st is None:
                    continue
                # 第 156-158 处：逐客户端隔离 —— 一个客户端处理/发送失败不饿死后面的（第 156 处实测我的客户端 cur 永远 0）；
                # 每 10 拍记谁被处理，好照实看清「谁在收、谁被跳过」。
                beat = globals().get("_mon_beat", 0) + 1
                globals()["_mon_beat"] = beat
                if beat % 10 == 1:
                    svc._log("monitor", "处理客户端 id=" + str(id(ws)) + " iv=" + str(st["interval"]) + " cur=" + str(len(st["cursor"])))
                try:
                    batch = []
                    for name in list(svc.SERVICES) + ["jarvis"]:  # 第 2 条：加爱莉希雅自己的日志环
                        part, new = svc.logs_since(name, st["cursor"].get(name, 0))
                        st["cursor"][name] = new
                        if part:
                            batch.append([name, part])
                    payload = {"type": "monitor", "data": snap, "logs": batch}
                    await ws.send_text(json.dumps(payload))
                except Exception as e2:
                    # 第 119 处 + 第 158 处自曝：原先 send 失败就 pop 客户端；改成落环 + 只在真断开时摘。
                    # 第 158 处的真 bug：原先 `except Exception:` 没有 as e，行内用 e 会 NameError。这里用 e2。
                    svc._log("monitor", "发送失败: " + repr(e2) + " client_state=" + str(getattr(ws, "client_state", None)))
                    if getattr(ws, "client_state", None) == 2:
                        _mon_state.pop(ws, None)
            await asyncio.sleep(max(0.0, max(1, _mon_interval) - (time.time() - t0)))
        except Exception as e:
            # 推送循环不能因一次采样/发送崩掉：记到日志区，下一拍继续
            svc._log("monitor", "推送循环异常: " + repr(e))
            # 第 134 处根因取证（第 141 处自曝）：只写异常名看不出是哪一行 —— KeyError(9880)
            # 查了半天，字面量 [9880] 不存在（只有 out[port]=… 与 .get(port)）。带上现场那一行。
            import traceback as _tb
            tail = [x for x in _tb.format_exc().split(chr(10)) if x.strip()]
            svc._log("monitor", "现场: " + " | ".join(tail[-6:]))
            await asyncio.sleep(1)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _clients.append(ws)
    await ws.send_text(json.dumps({"type": "connected", "message": "爱莉希雅已上线。"}))
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "chat":
                user_text = msg["text"]

                # "stop" typed in chat = abort everything
                from jarvis.main import _is_stop_command
                if _is_stop_command(user_text):
                    from jarvis.main import abort_all
                    abort_all()
                    await ws.send_text(json.dumps({"type": "response", "text": "已停止。"}))
                    continue

                from jarvis.main import _process_request, _Aborted, event_log
                loop = asyncio.get_event_loop()
                try:
                    response = await loop.run_in_executor(
                        None, _process_request, user_text, "web",
                    )
                    # The reply reaches clients via main._broadcast (registered
                    # event listener -> _broadcast_to_ws); no direct send needed.
                    from jarvis.main import _speak_streamed_if_unmuted
                    threading.Thread(target=_speak_streamed_if_unmuted, args=(response,), daemon=True).start()
                except _Aborted:
                    await ws.send_text(json.dumps({"type": "response", "text": "已停止。"}))
                except Exception as e:
                    # The failure must land in the event ledger, not only on this
                    # socket: /api/events and the 实时 panel are what a second tab,
                    # the 2 s poller and a page reload read. WS-only meant the run
                    # was invisible outside the tab that triggered it (HB-043,
                    # records/2026-11-16-12-33-59.md round 1).
                    text = f"Error: {e}"
                    try:
                        event_log.log("assistant", text, "web")
                    except Exception:
                        pass
                    await ws.send_text(json.dumps({"type": "response", "text": text}))

            elif msg.get("type") == "interrupt":
                from jarvis.main import abort_all
                abort_all()

            elif msg.get("type") == "monitor_config":
                # 间隔前端可调（Q30-3：最低 1 s）；页面隐藏时前端设 30 s 省 CPU
                iv = max(1, min(30, int(msg.get("interval", 5))))
                global _mon_interval  # 第 105 处自曝：少了 global，赋值变局部变量，节拍永远停在 5
                st = _mon_state.get(ws)
                _mon_state[ws] = {"interval": iv,
                                      "cursor": (st or {}).get("cursor", {})}
                _mon_interval = min(v["interval"] for v in _mon_state.values())

    except WebSocketDisconnect:
        if ws in _clients:
            _clients.remove(ws)
        _mon_state.pop(ws, None)
    except WebSocketDisconnected:
        _mon_state.pop(ws, None)  # 断连也要退出监控节拍（不留死客户端）
        # 11:56 自曝（record_9.md 轮 21-23）：驱动断开后 `ws.receive_text()` 抛的是
        # starlette 的 `WebSocketDisconnected`（「WebSocket is not connected. Need to call
        # "accept" first.」），不是 `WebSocketDisconnect`，这条 catch 接不住，每条断连
        # 都把栈刷进 ASGI 日志。接住它，断连不报错。
        if ws in _clients:
            _clients.remove(ws)


def start_web_background(port: int = 7860) -> None:
    """Launch web UI in a daemon thread. Non-blocking."""
    from jarvis.main import register_event_listener
    register_event_listener(_broadcast_to_ws)

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning")
        server = uvicorn.Server(config)
        loop.run_until_complete(server.serve())

    t = threading.Thread(target=_run, daemon=True)
    t.start()
