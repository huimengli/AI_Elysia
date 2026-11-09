"""Jarvis Web UI — runs alongside voice as a background thread."""
from __future__ import annotations
import asyncio
import json
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse

from jarvis.tts import speak_streamed, stop_speaking, is_speaking

_STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Jarvis")
_clients: list[WebSocket] = []
_loop: asyncio.AbstractEventLoop | None = None


# ─── Capture the REAL event loop at startup ───

@app.on_event("startup")
async def _capture_loop():
    global _loop
    _loop = asyncio.get_running_loop()
    print("[Web] Event loop captured — WebSocket broadcast ready.")


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
        except Exception:
            if ws in _clients:
                _clients.remove(ws)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse((_STATIC_DIR / "index.html").read_text(encoding="utf-8"))


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
    return JSONResponse({
        "tts": cfg.get("tts", {}),
        "stt": cfg.get("stt", {}),
        "wake_word": cfg.get("wake_word", {}),
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
    if "wake_word" in body:
        cfg.setdefault("wake_word", {}).update(body["wake_word"])
    if "context" in body:
        cfg.setdefault("context", {}).update(body["context"])
    if "llm" in body:
        if "temperature" in body["llm"]:
            cfg.setdefault("llm", {})["temperature"] = body["llm"]["temperature"]
    if "tools" in body:
        cfg.setdefault("tools", {}).update(body["tools"])

    _save_config(cfg)
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


def _tcp_probe(host: str, port: int, timeout: float = 0.8) -> bool:
    """True when something is listening on host:port (loopback probes are cheap)."""
    if not host or port <= 0:
        return False
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


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
    asr = {
        "online": True,
        "warm": loaded,
        "model": stt_cfg.get("model", "small"),
        "language": stt_cfg.get("language", "zh"),
        "device": device or stt_cfg.get("device", "cpu"),
        "detail": (
            f"faster-whisper {stt_cfg.get('model', 'small')} / "
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

                from jarvis.main import _process_request, _Aborted
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
                    await ws.send_text(json.dumps({"type": "response", "text": f"Error: {e}"}))

            elif msg.get("type") == "interrupt":
                from jarvis.main import abort_all
                abort_all()

    except WebSocketDisconnect:
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
