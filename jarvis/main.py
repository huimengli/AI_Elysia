from __future__ import annotations
import json
import re
import sys
import time
import os
import atexit
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
from jarvis.stt import record_until_silence, transcribe_audio, set_abort_event, set_hot_words
from jarvis.tts import speak, speak_streamed, is_speaking, stop_speaking, play_ack_wav, play_ack_phrase, preload_ack_audio
from jarvis.context import ContextManager
from jarvis.memory import Memory
from jarvis.events import EventLog
from jarvis.tools.router import TOOL_SCHEMAS, dispatch, tool_label

_MAX_TOOL_LOOPS = 3
_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def register_clean_exit_hook() -> None:
    """HB-049（records/2026-11-21-10-39-00.md 第 1 项）。

    `JARVIS_TAG` 存在时写 `.tmp/<tag>.clean_exit`，让看门狗的判据成立：**码 0 且标记在 = jarvis
    自己收尾；码 0 且标记不在 = 被外部终止**（不是正常收尾）。`atexit` 覆盖 sys.exit 与异常退出；
    被 `TerminateProcess` 杀掉的进程**不会**跑 atexit，所以标记必然不在 —— 这正是「被杀」的第一手。
    """
    tag = os.environ.get("JARVIS_TAG")
    if not tag:
        return
    path = Path(__file__).parent.parent / ".tmp" / (tag + ".clean_exit")
    path.parent.mkdir(parents=True, exist_ok=True)
    def _write() -> None:
        try:
            path.write_text(time.strftime("%Y-%m-%d %H:%M:%S") + " clean_exit（atexit）", encoding="utf-8")
        except Exception:
            pass
    atexit.register(_write)
    print(f"[watchdog] clean_exit marker armed: {path}")

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
    was_set = _abort.is_set()
    _abort.set()
    # Name the caller: the 0.3s captures in records/2026-11-08-19-25-48.md
    # gave no way to tell who set the flag mid-recording (wake barge-in, UI 中止,
    # WS interrupt, Esc all look identical in the log).
    import traceback
    frames = traceback.extract_stack()[:-1]
    site = frames[-1] if frames else None
    print(f"[ABORT] set by {site.name}:{site.lineno} thread={threading.current_thread().name}" if site else "[ABORT] set")
    stop_speaking()
    # Broadcast 已停止。 only on the unset→set transition. The user's own
    # speech scores 0.65-0.78 around the wake threshold, so a single turn used to
    # fire abort_all() two/three times and the UI got 2-3 「已停止」 bubbles
    # (records/2026-11-08-20-44-17).
    if not was_set:
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


def _looks_understandable(text: str) -> bool:
    """Guard against degenerate STT output. With language forced to English the
    user's Chinese speech came back as literal "You" (records/2026-11-08-18-54-18),
    which the LLM answered with a bare "Done.". Text without CJK characters and
    shorter than a sentence is "didn't catch", not a request.
    """
    t = text.strip()
    if any("\u4e00" <= ch <= "\u9fff" for ch in t):
        return True
    return len(t) > 20


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


def _ask_repeat_if_unmuted() -> None:
    """「我没听清，请再说一遍」——优先播 RAM 里预合成的具名 ack（`ack_no_heard.wav`），
    缓存缺该句时才回退 live TTS（records/2026-11-12-23-08-34.md）。

    只在**空转录**与**低质量转录**两个分支调用，不是每次唤醒都播；
    `stop_speaking()` / barge-in 语义不变（`play_ack_phrase` 走同一条复用输出流与 `_interrupt`）。
    """
    if _muted.is_set():
        return
    if play_ack_phrase("ack_no_heard"):
        return
    speak("我没听清，请再说一遍。")


def _record_hot_phrase(text: str) -> None:
    """写入 `hot_phrases`（records/2026-11-11-21-36-30.md 第 2 项），并按配置回灌偏置。

    - `user`：真实转录成功的整句；
    - `near_miss`：含唤醒词近音的句（与「爱莉希雅」的 difflib 相似度在 0.5-0.9，
      实测的误识形如 爱丽安娜 / 爱丽丝 / 米希雅 / 泰利西亚，可导出成训练与验收数据）；
    - **偏置默认关闭**（`stt.hot_bias: false`）：第 3 轮 A/B 实测，把热词灌进 whisper 的
      `initial_prompt` 会让**短句被吸附到热词**（`爱丽安娜`→「爱莉希雅」sim 0.25、
      `爱丽丝`→「爱莉希。」sim 0.29，两件变差），所以表只作为数据源（统计 + 训练导出），
      只有显式 `stt.hot_bias: true` 才灌进 prompt。
    """
    import difflib

    t = text.strip()
    if not t:
        return
    try:
        memory.record_phrase(t, "user")
        best = max((difflib.SequenceMatcher(None, w, t).ratio()
                    for w in re.findall(r"[\u4e00-\u9fff]{2,5}", t)), default=0.0)
        if 0.5 <= best < 0.9:
            memory.record_phrase(t, "near_miss")
        if _load_config().get("stt", {}).get("hot_bias", False):
            set_hot_words(memory.top_hot_phrases(12))
        else:
            set_hot_words([])
        print(f"[热词] 表 {len(memory.hot_phrase_rows())} 行，偏置={'开' if _load_config().get('stt', {}).get('hot_bias', False) else '关'}")
    except Exception as e:
        print(f"[热词] 记录失败（不影响对话）：{e}")


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

# 本机常用应用表（records/2026-11-13-13-46-12.md）：open_app 先匹配这张表。
# 幂等灌入，失败不阻塞启动（表已存在时只是跳过，扫描一次约 2 s）。
try:
    from jarvis.apps import populate as _populate_apps
    _apps_stats = _populate_apps()
    print(f"[Apps] {_apps_stats}")
except Exception as e:
    print(f"[Apps] WARN: 应用表灌入失败，open_app 将只走其它路径：{e}")


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
        "Routing for 打开 X (records/2026-11-18-10-17-23.md):\n"
        "- 打开浏览器 / 打开github / 打开b站 / 打开百度 / 打开任何站点名（含用户自定义对象名）"
        "→ **open_site**; never open_app for a web page (open_app for a web name matches the "
        "app table and lands on nonsense like a Sandboxie launcher, measured 10:41 round 1).\n"
        "- 打开微信/记事本/notepad 这类**桌面程序** → open_app; if it reports a launcher stub "
        "or several candidates, report that plainly, do not pick one yourself.\n"
        "- 搜索 → web_search (it opens baidu, bing fallback); 暂停播放/恢复播放/关闭音乐 → music_control.\n"
        "- 暂停播放 / 恢复播放 / 关闭音乐 = **only `music_control`** (pause/resume/close). The tool "
        "refuses `media_control`, `click_at`, `press_key`, `scroll_screen`, `type_text`, `run_python` "
        "under these words (measured 11:44: after a refusal the model clicked (0,0) and pressed "
        "ctrl+c; the video was never paused). If `music_control` is refused, report the refusal — "
        "do not improvise an action.\n"
        "- 搜索/查询类请求**只调用 web_search**：不要顺手播歌。`play_music` 只在用户明确说"
        "播放/听歌/放歌/来一首时才调用（11:07 实测：用户说「搜索 爱莉希雅 歌曲」，模型自作主张"
        "调 play_music(keyword='爱莉希雅') 把搜索页换成视频播放，这是越界）。\n"
        "- 要看我起的浏览器窗口的内容用 `read_page`（CDP 读 DOM 文本，带标题+地址复读）；"
        "要在页面里找字/点链接用 `find_on_page` / `click_page_text`（DOM 文本匹配 + CDP 受信点击）。"
        "**这台机器没有可用中文 OCR**（WinRT OCR 不可用、Umi-OCR 未安装），`read_screen`/"
        "`find_on_screen` 对中文必然找不到（12:00 实测「屏幕上找不到『打开浏览器』」），"
        "浏览器内容一律走 CDP，不要拿它凑数。**不要 `run_python` 抓网页**（11:14 实测模型写 bs4，"
        "`ModuleNotFoundError`，结果一个没拿到）。需要时间/日期才调 get_time，没被问不要调。\n"
        "- Stop after the tool gives evidence; do not pad with get_open_windows / press_key / "
        "run_python once the result is in hand.\n\n"
        "Always reply in Simplified Chinese (简体中文) unless the user explicitly asks for another language. "
        "Answer in 1-3 sentences unless more is clearly needed. "
        "For 现在几点 / 今天几号 / 日期 questions call get_time, never get_weather. "
        "After a tool call, report the outcome as one short Chinese sentence — "
        "never answer with a bare 'Done.', 'OK' or '已完成'; the user hears this text, "
        "so it must say what you did. "
        "NEVER invent a tool result, a file, a web page, or an action you did not "
        "perform. If a tool fails, say plainly 「XX 失败了：<原因>」 and stop; do not "
        "describe tools you did not call. If the user's speech looks like fragments "
        "(numbers with no question, half words), ask them to repeat instead of "
        "guessing what they meant. "
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
    executed: list[tuple[str, str]] = []
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
                _broadcast({"type": "tool", "name": call["function"]["name"], "label": tool_label(call["function"]["name"]), "args": args})
                if tool_count == 4:
                    _speak_if_unmuted("好的，我处理一下。")
                result = _exec_tool_with_retry(call["function"]["name"], args)
                executed.append((call["function"]["name"], result))
                # 2026-11-17 19:35 fix (`tests/2026-11-17-18-46-00_cc/record_3.md` 轮 3):
                # `result[:120]` cut the report right before the failure reason, so the
                # end-to-end round could not be root-caused from jarvis' own log. Full text
                # goes to the log; the WS/UI keeps its 200-char cap.
                print(f"[Tool: {call['function']['name']}] " + result.replace("\n", " | "))
                _broadcast({"type": "tool_result", "name": call["function"]["name"], "label": tool_label(call["function"]["name"]), "result": result[:200]})
                full_messages.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": call["id"],
                })
        else:
            # A bare "Done." was the literal fallback here: Qwen returns content=""
            # after a tool round, so the user heard "Done." for every tool task
            # (records/2026-11-08-18-54-18.md). Report what actually ran.
            txt = _strip_think("".join(content_parts))
            if txt.strip() in {"Done.", "Done", "OK", "ok", "已完成"}:
                txt = ""
            return txt or _tool_report(executed)
    return _tool_report(executed)


def _tool_report(executed: list[tuple[str, str]]) -> str:
    """Spoken report when the model returns empty content after tool rounds.

    Tool names are reported in Chinese (records/2026-11-09-21-55-14.md): the user
    heard "我执行了 type_text、press_key" before, which is unreadable when spoken.
    """
    if not executed:
        return "我处理好了。"
    names = "、".join(tool_label(n) for n, _ in executed)
    last = executed[-1][1].strip().split("\n")[0][:80]
    return f"我执行了 {names}：{last}"


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
                _broadcast({"type": "tool", "name": tc.function.name, "label": tool_label(tc.function.name), "args": args})
                if tool_count == 4:
                    _speak_if_unmuted("好的，我处理一下。")
                result = _exec_tool_with_retry(tc.function.name, args)
                print(f"[Tool: {tc.function['name'] if isinstance(tc, dict) else tc.function.name}] "
                      + result.replace("\n", " | "))
                _broadcast({"type": "tool_result", "name": tc.function.name, "label": tool_label(tc.function.name), "result": result[:200]})
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


_PLAY_VERBS = ("播放", "播", "放歌", "放一首", "来一", "听", "唱", "bgm", "音乐来")
_DANGER_WORDS = ("锁屏", "锁定", "锁屏", "关机", "重启", "休眠", "睡眠", "lock", "power", "shutdown", "reboot")
_last_user_text = [""]  # 可变容器：分发层的越界闸门读它
_PLAYED = [False]  # 本轮是否已播过一次歌（play_music 闸门）


def _exec_tool_with_retry(name: str, args: dict) -> str:
    """Execute a tool, retry once on failure."""
    # **硬闸门**（11:12 自曝，tests/2026-11-18-10-17-23_cc/record_5.md 轮 5/5b）：用户只说
    # 「搜索…」，2B 模型连着两轮自作主张调 `play_music`（还先补 media_control(pause)）。
    # 提示词压不住，所以在分发层拒绝执行——话里没有播放动词就不放歌，如实告诉模型。
    if name == "play_music":
        u = _last_user_text[0]
        if u and not any(v in u for v in _PLAY_VERBS):
            return (f"没有播歌：这句话里没有播放指令（原文「{u[:40]}」）。"
                    f"要播歌请说「播放…」「来一首…」「听…」；搜索/查询我不会自作主张放歌。")
        if u and u.startswith("打开") and any(v in u for v in ("页", "网站", "站点", "浏览器", "网")):
            # 11:56 自曝（record_9.md 轮 19）：「打开我的播歌页」里的「播」撞了 `_PLAY_VERBS`，
            # 闸门放行，模型真去播歌（BV11a411R7AM）而没打开 config.yaml 里的自定义对象
            # `我的播歌页`。这是**动词假阳性**：「打开 + …页/网站/浏览器」是开对象，不是播歌。
            return (f"没有播歌：「{u[:30]}」是**打开对象**的指令，该调 `open_site`"
                    "（用户自定义站点在 config.yaml 的 `sites:` 里，用户名字优先），"
                    "不是播放指令 —— 「播歌页」里的「播」撞了播放动词，我不拿它当播放。")
        if _PLAYED[0]:
            # 22:05 播歌唯一性 + 11:20 轮 6c 实测（模型连调两次 play_music，同一首歌
            # 从 0:00 播两遍，第二遍还多杀一次窗口）：一轮里只允许一次播放，第二次拒。
            return ("这一句已经播过一次歌了，**不再重复播放**（22:05 同一时刻只允许 1 个"
                    "播歌窗口）。第一次的证据已在上面，直接引用它回复。")
        _PLAYED[0] = True
    if name == "media_control":
        # 11:32 自曝（record_7.md 轮 7-10）：「暂停播放」「恢复播放」「关闭音乐」全被模型
        # 派给 `media_control`（系统媒体键，回「媒体操作已执行」但**没有回读**，证明不了
        # 当前视频被暂停），`music_control`（CDP 回读 paused）一次都没被调用。
        u = _last_user_text[0]
        if u and any(v in u for v in ("播放", "音乐", "视频", "暂停", "恢复", "关闭")) \
                and not any(v in u for v in ("下一首", "上一首", "静音", "音量")):
            return ("没有按系统媒体键：这句话是**播放控制**，请用 `music_control`"
                    "（pause 暂停 / resume 恢复 / close 关闭我自己起的窗口），"
                    "它会回读 `video.paused` 作证据；`media_control` 是系统媒体键，"
                    "「已执行」三个字证明不了当前视频被暂停。")
    if name in ("click_at", "press_key", "scroll_screen", "type_text", "run_python"):
        # 11:44 自曝（record_7.md 轮 8c）：`media_control` 被闸门挡回、提示让它用
        # `music_control`，模型转手调 `click_at (0,0)` + `press_key ctrl+c` 凑数，
        # 「暂停播放」始终没落到 CDP 回读。播放控制话术下不接受这类凑数动作。
        u = _last_user_text[0]
        site_open = u.startswith("打开") and any(v in u for v in ("页", "网站", "站点", "浏览器", "网", "github", "b站", "b 站"))
        if (u and any(v in u for v in ("播放", "音乐", "视频"))
                and any(v in u for v in ("暂停", "恢复", "关闭", "续播"))) or site_open:
            return (f"没有执行「{tool_label(name)}」：这句话是"
                    f"{'打开指定对象' if site_open else '播放控制'}（原文「{u[:40]}」），"
                    f"该调的是 {'`open_site`（自定义对象在 config.yaml `sites:`）' if site_open else '`music_control`（pause/resume/close）'}"
                    "，它会给出地址/标题或 `video.paused` 的回读证据。点坐标、按键、滚轮、敲字、"
                    "找屏幕、跑代码都不算打开/暂停/恢复/关闭。")
# 12:31 自曝（record_10.md 轮 26）：「在页面上找到『番剧』并点击」模型去 web_search +
    # 两次 run_python(bs4)（ModuleNotFoundError），一个链接都没读到，还把 b 站导航走。
    # 提示词压不住 2B 模型，所以这条走分发层：找字/点击类话术只准 find_on_page / click_page_text。
    if name in ("web_search", "run_python", "read_screen", "find_on_screen", "fetch_page"):
        u = _last_user_text[0]
        if u and ("点击" in u or "找到" in u) and ("页面" in u or "页" in u):
            return (f"没有执行「{tool_label(name)}」：这句话是在**我自己起的浏览器页面里**"
                    f"找字/点击（原文「{u[:40]}」），该调的是 `find_on_page` / `click_page_text`"
                    "（CDP 读 DOM + 受信点击，页面坐标）。这台机器没有中文 OCR，"
                    "bs4/requests 抓网页在这台机器没有装（实测 ModuleNotFoundError），"
                    "web_search 只会把页面导航走，不是点击。")

    if name == "kill_process":
        # Q29/Q32/Q34 只授权关**我自己起的 pid**。`kill_process("chrome")` 会连你
        # 自己的窗口一起杀（11:20 轮 6c 实测：模型在播完后自己补了这句）。
        tgt = str(args.get("name", "")).lower().removesuffix(".exe")
        if tgt in ("chrome", "msedge", "edge", "browser", "firefox"):
            return (f"没有杀 {args.get('name')}：`kill_process` 按进程名杀，会连**你自己**"
                    f"的浏览器窗口一起杀。授权范围（Q29/Q32/Q34）只允许我关**我自己起的"
                    f"pid**，播完的窗口由 `play_music` / `music_control(action=close)` 收尾。")
    # **危险工具闸门**（11:12 自曝，record_6.md 轮 6b）：没人让它锁屏，模型自己调了
    # `lock_screen`，回「已锁定屏幕。」——用户人不在电脑前。锁屏/关机/重启这类
    # **不可逆的系统操作只在用户话里明确出现时才允许执行。
    if name in ("lock_screen", "power_command"):
        u = _last_user_text[0]
        if u and not any(v in u for v in _DANGER_WORDS):
            return (f"没有执行「{tool_label(name)}」：这句话里没有锁屏/关机/重启的意思"
                    f"（原文「{u[:40]}」）。这类操作只在你明确说「锁屏/关机/重启」时才做。")
    t0 = time.time()
    result = dispatch(name, args)
    ok = not ("执行失败：" in result and result.startswith("工具「"))
    if not ok:
        time.sleep(0.5)
        result = dispatch(name, args)
    # E 块（design §2）：工具调用次数/耗时/失败率的埋点
    try:
        from jarvis import services as svc
        svc.tool_stat(name, ok, time.time() - t0)
    except Exception:
        pass
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
    global _stt_recording
    _abort.clear()
    # The barge-in guard (wake.py busy branch) checks is_recording() / is_speaking()
    # only. Traced live (job pwsh-44, records/2026-11-08-19-25-48.md): a trigger
    # landing in the ack window printed `barge-in score=0.664 recording=False`,
    # aborted, and the flag was still False — so record_until_silence died on its
    # first chunk (0.3s → "我没听清"). Mark the whole turn as busy here.
    _stt_recording = True
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
        _stt_recording = False
        _abort.clear()
        _broadcast({"type": "status", "message": "就绪。"})
        print("[爱莉希雅] Listening for wake word...")


def _handle_wake_inner() -> None:
    """唤醒流水线 + **音乐 ducking**（records/2026-11-18-10-17-23.md 第 1 项：「音乐播放时
    如果触发应该暂停音乐,录音结束后恢复(或直到'爱莉希雅'回复完成后恢复）」）。

    触发点 = 唤醒命中（不是录音结束）；恢复点 = 回复（TTS）播报完成后。`finally` 保证
    空转录、低质量转录、`_Aborted`（中止指令/打断）、异常都走恢复，**不许静音卡死**。
    只碰我自己起的窗口（CDP 9333 只在我起的实例上监听），没播放就如实说。
    """
    from jarvis.tools.browser_cdp import duck

    note = duck("pause")
    print(f"[Duck] {note}")
    try:
        _handle_wake_body()
    finally:
        print(f"[Duck] {duck('resume')}")


def _handle_wake_body() -> None:
    global _stt_recording
    # Mark the turn as recording from the very start: `is_recording()` gates the
    # wake barge-in abort (wake.py 121-132), and the flag used to be set only
    # after the 0.15s mic-release sleep — so a trigger landing in the ack window
    # saw is_recording() == False and called abort_all(), which cuts
    # record_until_silence on its first chunk (0.3s → "no voice recognized").
    _stt_recording = True
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

    # Clear a stale abort flag *before* recording. `record_until_silence`
    # checks the abort event every chunk (jarvis/stt.py), and `_abort` is only
    # cleared in `_process_request`, which runs after recording — so a flag left
    # over from the previous turn (wake during busy = abort_all, UI 中止, Esc)
    # cut captures to 0.3s: events.db rows 162-169 are wake → 0.3s → "no voice
    # recognized" (records/2026-11-08-19-25-48.md).
    _abort.clear()
    print("[爱莉希雅] Recording...")
    _broadcast({"type": "status", "message": "正在聆听…"})

    # Pause wake word mic so STT can use the hardware exclusively
    from jarvis.wake import pause_wake_mic, resume_wake_mic
    pause_wake_mic()
    time.sleep(0.15)  # Give pyaudio time to release the mic
    _stt_recording = True
    try:
        _stt_cfg = _load_config().get("stt", {})
        audio = record_until_silence(
            no_speech_seconds=float(_stt_cfg.get("no_speech_seconds", 2.0)),
        )
    finally:
        _stt_recording = False
        resume_wake_mic()  # Always resume wake word detection
    _check_abort()
    print(f"[爱莉希雅] Recorded {len(audio)/16000:.1f}s of audio, transcribing...")
    t_asr = time.time()
    user_text = transcribe_audio(audio)
    # F 块埋点（照实记耗时；tokens/s 未埋，那要 tokenizer）
    try:
        from jarvis import services as svc
        svc.metric("asr_secs", round(time.time() - t_asr, 2))
    except Exception:
        pass
    if not user_text.strip():
        print("[爱莉希雅] Transcription empty — didn't catch anything.")
        event_log.log("system", "Wake: no voice recognized", "voice")
        _ask_repeat_if_unmuted()  # 预合成 ack，不走 live TTS
        _broadcast({"type": "status", "message": "就绪。"})
        return
    print(f"[You] {user_text}")

    # 热词表写入 + 偏置回灌（records/2026-11-11-21-36-30.md 第 2 项）：
    # 真实转录成功后记 `user`；含唤醒词近音（sim 在 0.5-0.9 之间）记 `near_miss`；
    # 然后取 top-N 灌进 whisper 的 initial_prompt（下次转录生效）。
    _record_hot_phrase(user_text)

    if not _looks_understandable(user_text):
        print(f"[爱莉希雅] Low-quality transcription ({user_text!r}) — asking to repeat.")
        event_log.log("system", f"Wake: low-quality transcription: {user_text}", "voice")
        _ask_repeat_if_unmuted()  # 同上：预合成 ack
        _broadcast({"type": "status", "message": "就绪。"})
        return

    if _is_stop_command(user_text):
        event_log.log("system", f"Voice stop command: {user_text}", "voice")
        abort_all()
        print("[爱莉希雅] Stopped. (voice)")
        raise _Aborted()

    t_llm = time.time()
    response_text = _process_request(user_text)
    _check_abort()
    try:
        from jarvis import services as svc
        svc.metric("llm_secs", round(time.time() - t_llm, 2))
        svc.metric("llm_chars", len(response_text))
    except Exception:
        pass

    print(f"[爱莉希雅] {response_text}")
    _broadcast({"type": "status", "message": "正在说话…"})
    t_tts = time.time()
    _speak_streamed_if_unmuted(response_text)
    try:
        from jarvis import services as svc
        svc.metric("tts_secs", round(time.time() - t_tts, 2))  # 照实：含合成与播放全程
    except Exception:
        pass


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
    _last_user_text[0] = user_text  # 越界闸门读这份原文（main._exec_tool_with_retry）
    _PLAYED[0] = False  # 每句只允许一次 play_music（22:05 播歌唯一性）
    _broadcast({"type": "user", "text": user_text})
    _broadcast({"type": "status", "message": "思考中…"})

    facts = memory.search_facts(user_text)
    messages = context.get_messages()
    messages.append({"role": "user", "content": user_text})

    # Single system message: Qwen3.5/3.8 chat templates raise "System message must
    # be at the beginning" for any system turn that is not messages[0] (reproduced
    # against llama.cpp :8080 in records/2026-11-08-17-53-00.md). context.py prefixes
    # its rolling summary as a system turn, so strip it here and fold it into the
    # single system message together with the memory facts.
    leading: list[str] = []
    while messages and messages[0].get("role") == "system":
        leading.append(messages.pop(0).get("content", ""))
    sys_content = _system_prompt()
    if leading:
        sys_content += "\n\n" + "\n".join(leading)
    if facts:
        sys_content += "\n\nRelevant context from memory: " + "; ".join(facts)
    full_messages = [{"role": "system", "content": sys_content}] + messages

    try:
        response_text = _call_llm(full_messages)
    except _Aborted:
        raise
    except Exception as e:
        # Surface the primary failure (an Ollama connection error used to mask
        # the real cause, e.g. the chat-template 500 from a second system turn).
        print(f"[WARN] Primary provider failed ({e}), trying Ollama fallback")
        _broadcast({"type": "status", "message": f"主模型失败：{str(e)[:120]}，改用备用模型…"})
        event_log.log("system", f"Primary provider failed: {str(e)[:200]}", source)
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


def _warm_stt() -> None:
    """Load faster-whisper at startup so the first transcription is not the
    model-load moment, and the asr lamp's `warm` flips to true immediately."""
    try:
        t0 = time.perf_counter()
        from jarvis.stt import _get_model
        _get_model()
        print(f"[STT] whisper warmed in {1000 * (time.perf_counter() - t0):.0f} ms")
    except Exception as e:
        print(f"[WARN] STT warm-up failed (first transcription will fail): {e}")


def main() -> None:
    import webbrowser
    from jarvis.web import start_web_background

    print("[爱莉希雅] Starting up...")
    print("[爱莉希雅] Keys: Esc = stop | F2 = type | INSERT = mute/unmute")

    register_clean_exit_hook()  # HB-049：看门狗要的第一手证据
    # 单窗口模式（start_all_in_one.bat 设 JARVIS_ONE_WINDOW=1）：jarvis 作父进程起子服务，
    # 管道归 jarvis（design §1：只有父进程抓得到 stdout）。端口已占用 = 外部起，走接入识别，
    # 不重复起、不杀。旧版 start_all.bat 不设这个变量，行为与今天完全一致（§8 两版并存）。
    if os.environ.get("JARVIS_ONE_WINDOW") == "1":
        from jarvis.services import arm_shutdown, launch
        for _name in ("llama", "tts"):
            print("[Monitor] " + json.dumps(launch(_name), ensure_ascii=False))
        arm_shutdown()
    start_web_background(port=7860)
    print("[爱莉希雅] Web UI: http://localhost:7860")

    threading.Thread(target=_keyboard_listener, daemon=True).start()
    # Load whisper in the background as soon as the server is up: the model lives
    # in the repo-local .hf-cache, and a missing HF_HOME/HF_ENDPOINT is what made
    # faster-whisper try to reach huggingface.co and die with ConnectError 10054.
    threading.Thread(target=_warm_stt, daemon=True).start()

    if os.environ.get("JARVIS_ONE_WINDOW") == "1":
        # design §7 第 7 条：jarvis 起自己的浏览器窗口开 /monitor（不最大化，窗口数走同一条口径）
        try:
            from jarvis.tools.app_control import open_url
            print("[Monitor] " + open_url("http://127.0.0.1:7860/monitor"))
        except Exception as e:
            print(f"[Monitor] 自起窗口打不开（{e!r}）— 退回默认浏览器，照实不假装成功")
            webbrowser.open("http://localhost:7860/monitor")
    else:
        webbrowser.open("http://localhost:7860")

    event_log.log("system", "爱莉希雅 online", "startup")
    # Warm the wake-ack path before the first turn: cached PCM + one open output
    # stream, so the first wake answer costs no file decode and no stream startup.
    try:
        preload_ack_audio()
    except Exception as e:
        print(f"[WARN] ack preload failed (will fall back to live TTS): {e}")
    try:
        _speak_if_unmuted("早安，爱莉希雅已上线。")
    except Exception as e:
        # Best-effort greeting: a missing/unready TTS backend must not kill the server.
        print(f"[WARN] Startup greeting failed (TTS unavailable?): {e}")
    listen_for_wake_word(handle_wake)


if __name__ == "__main__":
    main()
