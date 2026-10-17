from __future__ import annotations
import json
import re
import sys
import time
import threading
import msvcrt
from datetime import datetime
from pathlib import Path
import yaml
import numpy as np
import sounddevice as sd
import ollama
from openai import OpenAI

# Windows consoles default to GBK; LLM/tool output can contain characters GBK
# cannot encode (e.g. Qwen thinking marker U+21B5). Reconfigure so a print
# never crashes the process and masks the real error (HB-012).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from jarvis.wake import listen_for_wake_word
from jarvis.stt import record_until_silence, transcribe_audio, set_abort_event
from jarvis.tts import speak, speak_streamed, is_speaking, stop_speaking, play_ack_wav
from jarvis.context import ContextManager
from jarvis.memory import Memory
from jarvis.events import EventLog
from jarvis.tools.router import TOOL_SCHEMAS, dispatch

_MAX_TOOL_LOOPS = 3
_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

# Global abort — Esc sets this, stops everything (speech + tool loop + follow-up)
_abort = threading.Event()
set_abort_event(_abort)  # Let STT check abort during recording
# Global mute — INSERT toggles this, skips TTS when set
_muted = threading.Event()

# --- Message bus: push events to all connected web clients ---
_event_listeners: list = []  # list of callables: fn(event_dict)


def register_event_listener(fn) -> None:
    _event_listeners.append(fn)


def _broadcast(event: dict) -> None:
    for fn in _event_listeners:
        try:
            fn(event)
        except Exception:
            pass


class _Aborted(Exception):
    """Raised when user hits Esc to abort the current action."""
    pass


def abort_all() -> None:
    """Stop everything 爱莉希雅 is doing right now."""
    _abort.set()
    stop_speaking()
    _broadcast({"type": "status", "message": "已停止。"})


def _is_stop_command(text: str) -> bool:
    """Check if transcribed text is a voice stop command."""
    cleaned = text.strip().lower().rstrip(".,!?")
    return cleaned in {
        "stop", "jarvis stop", "hey jarvis stop",
        "cancel", "abort", "shut up", "be quiet", "nevermind", "never mind",
        # 中文语音停止命令（STT 转写结果，见 T1 2026-10-13-21-38-01）
        "停止", "停下", "爱莉希雅停止", "别说了", "闭嘴", "取消",
    }


def _check_abort() -> None:
    """Raise _Aborted if user requested abort."""
    if _abort.is_set():
        raise _Aborted()


def is_muted() -> bool:
    return _muted.is_set()


def toggle_mute() -> None:
    if _muted.is_set():
        _muted.clear()
        _broadcast({"type": "mute", "muted": False})
        print("[爱莉希雅] Unmuted.")
    else:
        _muted.set()
        stop_speaking()
        _broadcast({"type": "mute", "muted": True})
        print("[爱莉希雅] Muted.")


def _speak_if_unmuted(text: str) -> None:
    """Speak text only if not muted."""
    if not _muted.is_set():
        speak(text)


def _speak_streamed_if_unmuted(text: str) -> None:
    """Speak streamed text only if not muted."""
    if not _muted.is_set():
        speak_streamed(text)


# --- OpenAI client cache (keyed by base_url) ---
_openai_clients: dict[str, OpenAI] = {}


def _get_openai_client(base_url: str, api_key: str = "lm-studio") -> OpenAI:
    if base_url not in _openai_clients:
        _openai_clients[base_url] = OpenAI(
            base_url=base_url, api_key=api_key, timeout=300.0,
        )
    return _openai_clients[base_url]


context = ContextManager()
memory = Memory()
event_log = EventLog()  # T7: operation log → sqlite (jarvis/data/events.db)


def _system_prompt() -> str:
    now = datetime.now().strftime("%A, %B %d %Y, %I:%M %p")
    return (
        "You are 爱莉希雅, a fully agentic personal AI assistant with screen vision and desktop control. "
        "Be concise, confident, and helpful. No moralizing, no refusals, no disclaimers. "
        "Just do what your owner asks.\n\n"
        "AGENTIC WORKFLOW for UI tasks:\n"
        "1. focus_window — bring app to front\n"
        "2. find_on_screen — locate text/buttons (returns x,y coordinates)\n"
        "3. click_at — click the coordinates\n"
        "4. Wait 1-2s for UI to update, then read_screen or find_on_screen to verify\n"
        "5. Repeat until task is done. You can chain up to 15 tool calls.\n\n"
        "TIPS:\n"
        "- After clicking, always verify the result before proceeding\n"
        "- If text not found, try scroll_screen then find_on_screen again\n"
        "- For typing in fields: click_at the field first, then type_text\n"
        "- Use press_key for keyboard shortcuts (ctrl+t, alt+f4, etc)\n"
        "- If a tool fails, try once more before giving up\n\n"
        "Always reply in Simplified Chinese (简体中文) unless the user explicitly asks for another language. "
        "Answer in 1-3 sentences unless more is clearly needed. "
        f"Current date and time: {now}."
    )


def _load_config() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_config(cfg: dict) -> None:
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)


def get_providers() -> dict:
    """Return the providers dict from config."""
    cfg = _load_config()
    return cfg.get("llm", {}).get("providers", {})


def get_active_provider() -> str:
    """Return the active provider key."""
    cfg = _load_config()
    return cfg.get("llm", {}).get("active_provider", "ollama")


def set_active_provider(provider_key: str) -> bool:
    """Switch the active provider. Returns True on success."""
    cfg = _load_config()
    providers = cfg.get("llm", {}).get("providers", {})
    if provider_key not in providers:
        return False
    cfg["llm"]["active_provider"] = provider_key
    _save_config(cfg)
    _broadcast({"type": "provider_changed", "provider": provider_key})
    return True


def _play_beep() -> None:
    """Short beep to signal processing has started."""
    try:
        t = np.linspace(0, 0.12, int(24000 * 0.12), endpoint=False)
        tone = 0.3 * np.sin(2 * np.pi * 600 * t).astype(np.float32)
        sd.play(tone, samplerate=24000)
        sd.wait()
    except Exception:
        pass


def _strip_think(text: str) -> str:
    """Remove <think>...</response> blocks and stray Qwen thinking markers."""
    text = re.sub(r"<think>.*?</response>", "", text, flags=re.DOTALL)
    # Stray thinking tokens (U+21B5 / U+21B6) that can leak into the answer.
    text = text.replace("↵", "").replace("↶", "")
    return text.strip()


def _parse_tool_args(raw) -> dict:
    """OpenAI returns JSON string, Ollama returns dict. Handle both."""
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


_STREAM_STALL_TIMEOUT_S = 120.0


def _iter_stream_with_timeout(stream, timeout: float = _STREAM_STALL_TIMEOUT_S):
    """Yield chunks from an OpenAI stream, raising TimeoutError if no chunk
    arrives within ``timeout`` seconds.

    A dead or half-closed socket (e.g. llama-server dropping the connection
    mid-generation) otherwise blocks the iterator forever — see HB-014.
    """
    import queue
    import threading

    q: "queue.Queue" = queue.Queue()

    def _pump() -> None:
        try:
            for c in stream:
                q.put(c)
        except Exception as e:  # surface the transport error to the consumer
            q.put(e)
        finally:
            q.put(None)

    threading.Thread(target=_pump, daemon=True).start()
    while True:
        item = q.get(timeout=timeout)
        if item is None:
            return
        if isinstance(item, Exception):
            raise item
        yield item


def _call_openai_provider(provider_cfg: dict, temperature: float, full_messages: list[dict], max_tokens: int = 2048, enable_thinking: bool = False) -> str:
    """Call any OpenAI-compatible provider (LM Studio, NVIDIA NIM, etc.).

    Uses streaming so slow local generation is not killed by a single
    read-timeout, and abort checks run per chunk. max_tokens caps output;
    enable_thinking controls Qwen3-style thinking via llama.cpp chat_template_kwargs.
    """
    model = provider_cfg["model"]
    base_url = provider_cfg["base_url"]
    api_key = provider_cfg.get("api_key", "lm-studio")
    client = _get_openai_client(base_url, api_key)
    tool_count = 0
    for _ in range(_MAX_TOOL_LOOPS):
        _check_abort()
        stream = client.chat.completions.create(
            model=model,
            messages=full_messages,
            tools=TOOL_SCHEMAS,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
            stream=True,
        )
        content_parts: list[str] = []
        tool_acc: dict[int, dict] = {}  # index -> {id, name, arguments}
        for chunk in _iter_stream_with_timeout(stream):
            _check_abort()
            if not getattr(chunk, "choices", None):
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                content_parts.append(delta.content)
            tcs = getattr(delta, "tool_calls", None)
            if tcs:
                for tc in tcs:
                    slot = tool_acc.setdefault(
                        tc.index, {"id": "", "name": "", "arguments": ""}
                    )
                    if tc.id:
                        slot["id"] = tc.id
                    fn = tc.function
                    if fn is not None:
                        if fn.name:
                            slot["name"] += fn.name
                        if fn.arguments:
                            slot["arguments"] += fn.arguments

        if tool_acc:
            calls = [
                {
                    "id": s.get("id") or f"call_{i}",
                    "type": "function",
                    "function": {"name": s["name"], "arguments": s["arguments"]},
                }
                for i, s in sorted(tool_acc.items())
            ]
            full_messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": calls,
            })
            for call in calls:
                _check_abort()
                args = _parse_tool_args(call["function"]["arguments"])
                tool_count += 1
                _broadcast({"type": "tool", "name": call["function"]["name"], "args": args})
                if tool_count == 4:
                    _speak_if_unmuted("好的，我处理一下。")
                result = _exec_tool_with_retry(call["function"]["name"], args)
                print(f"[Tool: {call['function']['name']}] {result[:120]}")
                _broadcast({"type": "tool_result", "name": call["function"]["name"], "result": result[:200]})
                full_messages.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": call["id"],
                })
        else:
            return _strip_think("".join(content_parts) or "Done.")
    return "Done."


def _call_ollama_provider(provider_cfg: dict, temperature: float, full_messages: list[dict]) -> str:
    """Call Ollama provider."""
    model = provider_cfg["model"]
    tool_count = 0
    for _ in range(_MAX_TOOL_LOOPS):
        _check_abort()
        response = ollama.chat(model=model, messages=full_messages, tools=TOOL_SCHEMAS)
        if response.message.tool_calls:
            full_messages.append(response.message.model_dump())
            for tc in response.message.tool_calls:
                _check_abort()
                args = _parse_tool_args(tc.function.arguments)
                tool_count += 1
                _broadcast({"type": "tool", "name": tc.function.name, "args": args})
                if tool_count == 4:
                    _speak_if_unmuted("好的，我处理一下。")
                result = _exec_tool_with_retry(tc.function.name, args)
                print(f"[Tool: {tc.function.name}] {result[:120]}")
                _broadcast({"type": "tool_result", "name": tc.function.name, "result": result[:200]})
                full_messages.append({
                    "role": "tool",
                    "content": result,
                    "name": tc.function.name,
                })
        else:
            return _strip_think(response.message.content or "Done.")
    return "Done."


def _call_llm(full_messages: list[dict]) -> str:
    """Route to the active provider."""
    cfg = _load_config()
    llm_cfg = cfg["llm"]
    temperature = llm_cfg.get("temperature", 0.7)
    max_tokens = int(llm_cfg.get("max_tokens", 2048))
    enable_thinking = bool(llm_cfg.get("enable_thinking", False))
    active = llm_cfg.get("active_provider", "ollama")
    providers = llm_cfg.get("providers", {})
    provider = providers.get(active, {})
    ptype = provider.get("type", "ollama")

    if ptype == "openai":
        return _call_openai_provider(provider, temperature, full_messages, max_tokens, enable_thinking)
    else:
        return _call_ollama_provider(provider, temperature, full_messages)


def _exec_tool_with_retry(name: str, args: dict) -> str:
    """Execute a tool, retry once on failure."""
    result = dispatch(name, args)
    if result.startswith("Tool '") and "failed:" in result:
        time.sleep(0.5)
        result = dispatch(name, args)
    return result


# Set while the wake pipeline is recording from the mic. wake.py uses this
# to suppress barge-in aborts: a trigger arriving mid-recording comes from
# the same microphone (the user's own speech / ambient noise), not a new
# turn, so aborting would kill our own capture and any in-flight web turn.
_stt_recording = False


def is_recording() -> bool:
    return _stt_recording


def handle_wake() -> None:
    """Called when wake word is detected. Full pipeline: listen → think → speak."""
    _abort.clear()
    try:
        _handle_wake_inner()
    except _Aborted:
        print("[爱莉希雅] Aborted.")
    except Exception as e:
        import traceback
        print(f"[ERROR] {e}")
        traceback.print_exc()
        event_log.log("system", f"Pipeline error: {e}", "error")
        if not _abort.is_set():
            _speak_if_unmuted("抱歉，出了点问题。")
    finally:
        _abort.clear()
        _broadcast({"type": "status", "message": "就绪。"})
        print("[爱莉希雅] Listening for wake word...")


def _handle_wake_inner() -> None:
    if is_speaking():
        stop_speaking()
    print("[爱莉希雅] Wake word detected!")
    event_log.log("wake", "Wake word triggered", "voice")
    _broadcast({"type": "status", "message": "在。"})
    _broadcast({"type": "wake", "text": "Wake word triggered"})
    if _muted.is_set():
        print("[爱莉希雅] (muted) skipping ack")
    else:
        play_ack_wav()  # T8: pre-synthesized local wav, no live SoVITS

    print("[爱莉希雅] Recording...")
    _broadcast({"type": "status", "message": "正在聆听…"})

    # Pause wake word mic so STT can use the hardware exclusively
    from jarvis.wake import pause_wake_mic, resume_wake_mic
    pause_wake_mic()
    time.sleep(0.15)  # Give pyaudio time to release the mic
    global _stt_recording
    _stt_recording = True
    try:
        audio = record_until_silence()
    finally:
        _stt_recording = False
        resume_wake_mic()  # Always resume wake word detection
    _check_abort()
    print(f"[爱莉希雅] Recorded {len(audio)/16000:.1f}s of audio, transcribing...")
    user_text = transcribe_audio(audio)
    if not user_text.strip():
        print("[爱莉希雅] Transcription empty — didn't catch anything.")
        event_log.log("system", "Wake: no voice recognized", "voice")
        _speak_if_unmuted("我没听清，请再说一遍。")
        _broadcast({"type": "status", "message": "就绪。"})
        return
    print(f"[You] {user_text}")

    if _is_stop_command(user_text):
        event_log.log("system", f"Voice stop command: {user_text}", "voice")
        abort_all()
        print("[爱莉希雅] Stopped. (voice)")
        raise _Aborted()

    response_text = _process_request(user_text)
    _check_abort()

    print(f"[爱莉希雅] {response_text}")
    _broadcast({"type": "status", "message": "正在说话…"})
    _speak_streamed_if_unmuted(response_text)


def _process_request(user_text: str, source: str = "voice") -> str:
    """Build context, call LLM, update memory. Returns response text.

    source: "voice" (wake pipeline / F2 keyboard) or "web" (WS chat).
    """
    # A new request always starts from a clean slate: an abort raised in a
    # previous turn (Esc / stop command / barge-in / WS interrupt) must not
    # poison this one. Mid-turn aborts are set *after* this line, so Esc
    # during LLM streaming still works as before.
    _abort.clear()
    _check_abort()
    _play_beep()
    event_log.log("user", user_text, source)
    _broadcast({"type": "user", "text": user_text})
    _broadcast({"type": "status", "message": "思考中…"})

    facts = memory.search_facts(user_text)
    messages = context.get_messages()
    messages.append({"role": "user", "content": user_text})

    # Single system message: Qwen3.8's chat template rejects a second system
    # message ("System message must be at the beginning"), so merge memory
    # facts into the main system prompt instead of a separate system turn.
    sys_content = _system_prompt()
    if facts:
        sys_content += "\n\nRelevant context from memory: " + "; ".join(facts)
    full_messages = [{"role": "system", "content": sys_content}] + messages

    try:
        response_text = _call_llm(full_messages)
    except _Aborted:
        raise
    except Exception as e:
        print(f"[WARN] Primary provider failed ({e}), trying Ollama fallback")
        cfg = _load_config()
        ollama_provider = cfg["llm"]["providers"].get("ollama", {"model": "qwen3:8b"})
        response_text = _call_ollama_provider(ollama_provider, cfg["llm"].get("temperature", 0.7), full_messages)

    context.add("user", user_text)
    context.add("assistant", response_text)
    event_log.log("assistant", response_text, source)
    memory.extract_and_store_facts(response_text, user_text)

    _broadcast({"type": "response", "text": response_text})
    return response_text



def _keyboard_listener() -> None:
    """Background thread: Esc = abort, F2 = type command, INSERT = mute/unmute."""
    while True:
        try:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # Escape key
                if key == b'\x1b':
                    abort_all()
                    print("\n[爱莉希雅] Stopped. (Esc)")
                # Extended keys: F2 = 0x00+0x3c, INSERT = 0xe0+0x52
                elif key in (b'\x00', b'\xe0'):
                    special = msvcrt.getch()
                    if special == b'<':  # F2
                        print("\n[Type your command] ", end="", flush=True)
                        cmd = input()
                        if cmd.strip():
                            _handle_typed_command(cmd.strip())
                    elif special == b'R':  # INSERT
                        toggle_mute()
            time.sleep(0.05)
        except Exception:
            time.sleep(0.1)


def _handle_typed_command(text: str) -> None:
    """Process a typed command (same as voice, but from keyboard)."""
    _abort.clear()
    print(f"[You] {text}")
    try:
        response = _process_request(text)
        print(f"[爱莉希雅] {response}")
        _speak_streamed_if_unmuted(response)
    except _Aborted:
        print("[爱莉希雅] Stopped.")
    finally:
        _abort.clear()


def main() -> None:
    import webbrowser
    from jarvis.web import start_web_background

    print("[爱莉希雅] Starting up...")
    print("[爱莉希雅] Keys: Esc = stop | F2 = type | INSERT = mute/unmute")

    start_web_background(port=7860)
    print("[爱莉希雅] Web UI: http://localhost:7860")

    threading.Thread(target=_keyboard_listener, daemon=True).start()

    webbrowser.open("http://localhost:7860")

    event_log.log("system", "爱莉希雅 online", "startup")
    try:
        _speak_if_unmuted("早安，爱莉希雅已上线。")
    except Exception as e:
        # Best-effort greeting: a missing/unready TTS backend must not kill the server.
        print(f"[WARN] Startup greeting failed (TTS unavailable?): {e}")
    listen_for_wake_word(handle_wake)


if __name__ == "__main__":
    main()
