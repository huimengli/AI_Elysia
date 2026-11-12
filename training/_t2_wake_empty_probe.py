r"""空转录 / 低质量转录分支探针（records/2026-11-12-23-08-34.md 第 2 轮）。

**不碰麦克风、不碰 LLM**：把 `jarvis.main` 里的录音与转录 monkeypatch 成可控返回值，
跑 `handle_wake()` 的内层，记录走的是**具名预合成 ack** 还是 live TTS 回退，
并检查 `stop_speaking` / `is_speaking` / 广播事件序列与打断语义不变。

- `MODE=empty` → 转录返回空串（`Transcription empty` 分支）；
- `MODE=lowq` → 转录返回「嗯」（`_looks_understandable` 为假，低质量分支）；
- `MODE=normal` → 转录返回「爱莉希雅，帮我打开浏览器」，走正常路径（此时**不应**播「我没听清」）。

Run:  .venv\Scripts\python.exe training\_t2_wake_empty_probe.py
"""
import os
import sys

import numpy as np

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODE = os.environ.get("MODE", "empty")
FAKE_AUDIO = np.zeros(16000 * 3, np.float32)

import jarvis.main as M  # noqa: E402

played: list[str] = []
events: list[dict] = []
requests: list[str] = []


def _fake_record(no_speech_seconds: float = 2.0, **kw):
    return FAKE_AUDIO


def _fake_transcribe(audio):
    if MODE == "empty":
        return ""
    if MODE == "lowq":
        # `_looks_understandable`：有 CJK 就算能理解，所以低质量必须用**无 CJK 且 ≤20 字符**
        # 的退化输出（records/2026-11-08-18-54-18 实测的 literal "You"）
        return "you"
    return "爱莉希雅，帮我打开浏览器"


def _spy_play_ack_wav():
    played.append("轮播 ack（唤醒应答）")


def _spy_play_ack_phrase(name: str) -> bool:
    played.append(f"具名 ack[{name}]")
    return True  # 不走 live TTS


def _spy_speak(text: str) -> None:
    played.append(f"live TTS：{text!r}")


def _spy_broadcast(ev: dict) -> None:
    events.append(ev)


def _fake_process_request(user_text: str, source: str = "voice") -> str:
    """只测应答路径，不跑 LLM / 工具（第 2 轮实测：真跑会开 Edge、压死 :8080/:9880）。"""
    requests.append(user_text)
    return ""


def _noop_resume() -> None:
    pass


M.record_until_silence = _fake_record
M.transcribe_audio = _fake_transcribe
M.play_ack_wav = _spy_play_ack_wav
M.play_ack_phrase = _spy_play_ack_phrase
M.speak = _spy_speak
M._broadcast = _spy_broadcast
M._process_request = _fake_process_request
M.pause_wake_mic = _noop_resume
M.resume_wake_mic = _noop_resume
M._play_beep = _noop_resume


def main() -> int:
    M.preload = None
    played.clear()
    events.clear()
    M.handle_wake()
    print(f"[MODE={MODE}] 播放序列：{played}", flush=True)
    print(f"[MODE={MODE}] 事件：{[e.get('message') or e.get('type') for e in events]}", flush=True)
    no_heard = any("ack_no_heard" in p for p in played)
    if MODE in ("empty", "lowq"):
        print(f"[判据] 该播「我没听清」= {no_heard}（具名 ack 命中，未走 live TTS）", flush=True)
        return 0 if no_heard else 1
    print(f"[判据] 正常路径不应播「我没听清」= {not no_heard}", flush=True)
    return 0 if not no_heard else 1


if __name__ == "__main__":
    sys.exit(main())
