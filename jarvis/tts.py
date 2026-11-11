from pathlib import Path
import io
import queue
import random
import re
import urllib.parse
import urllib.request
import wave
import time
import yaml
import numpy as np
import sounddevice as sd
import threading

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def _load_config():
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _tts_cfg() -> dict:
    return _load_config().get("tts", {})

def _active_provider() -> str:
    """Resolve active TTS backend: 'kokoro' (default) or 'gptsovits'."""
    return _tts_cfg().get("provider", "kokoro")

_pipeline = None
_voice_tensor = None
_speaking = threading.Event()  # set while audio is playing
_interrupt = threading.Event()  # set to stop streaming

_LOCAL_PTH = Path.home() / "Downloads" / "kokoro-v1_0.pth"

def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kokoro import KPipeline, KModel
        repo_id = "hexgrad/Kokoro-82M"
        if _LOCAL_PTH.exists():
            kmodel = KModel(repo_id=repo_id, model=str(_LOCAL_PTH)).to("cpu").eval()
            _pipeline = KPipeline(lang_code="a", repo_id=repo_id, model=kmodel)
        else:
            _pipeline = KPipeline(lang_code="a", repo_id=repo_id)
    return _pipeline

def _get_voice():
    """Load voice tensor once and cache it."""
    global _voice_tensor
    if _voice_tensor is None:
        import torch
        cfg = _load_config()
        voice_name = cfg["tts"]["voice"]
        local_voice = _LOCAL_PTH.parent / f"{voice_name}.pt"
        if local_voice.exists():
            _voice_tensor = torch.load(str(local_voice), weights_only=True)
        else:
            from huggingface_hub import hf_hub_download
            path = hf_hub_download(
                repo_id="hexgrad/Kokoro-82M",
                filename=f"voices/{voice_name}.pt",
                local_files_only=True,
            )
            _voice_tensor = torch.load(path, weights_only=True)
    return _voice_tensor


def _gptsovits_synth(text: str) -> tuple[bytes, int]:
    """Synthesize via GPT-SoVITS api_v2 TTS endpoint.

    Returns (int16 PCM bytes, sample_rate). Server returns a 24 kHz WAV.
    """
    cfg = _tts_cfg().get("gptsovits", {})
    api_url = cfg.get("api_url", "http://127.0.0.1:9880/tts")
    params = {
        "text": text,
        "text_lang": cfg.get("text_lang", "zh"),
        "ref_audio_path": cfg.get("ref_audio_path", ""),
        "prompt_lang": cfg.get("prompt_lang", "zh"),
        "prompt_text": cfg.get("prompt_text", ""),
        "speed_factor": float(cfg.get("speed_factor", 1.0)),
        "text_split_method": "cut5",
    }
    url = f"{api_url}?{urllib.parse.urlencode(params)}"
    timeout = float(cfg.get("timeout_s", 120))
    with urllib.request.urlopen(url, timeout=timeout) as r:
        wav_bytes = r.read()
    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    return pcm, rate


def _synth(text: str) -> tuple[bytes, int]:
    """Synthesize text with the active TTS provider. Returns (PCM int16 bytes, rate)."""
    if _active_provider() == "gptsovits":
        return _gptsovits_synth(text)
    pipeline = _get_pipeline()
    voice = _get_voice()
    speed = _tts_cfg().get("speed", 1.0)
    audio_chunks = []
    for _, _, audio in pipeline(text, voice=voice, speed=speed):
        if audio is not None:
            audio_chunks.append(audio)
    if not audio_chunks:
        return b"", 24000
    combined = np.concatenate(audio_chunks)
    pcm = (combined * 32767).astype(np.int16)
    return pcm.tobytes(), 24000


def _split_sentences(text: str) -> list[str]:
    """Split text into speakable segments on **Chinese and Latin punctuation**.

    The old regex `(?<=[.!?])\\s+` only split on Latin `.!?` followed by whitespace,
    so Chinese replies (「你好呀，我在听。今天…」) came out as **one** segment: SoVITS
    had to synthesize the whole answer before the first sound, which is what made
    TTS feel slow. Splitting on 「，。！？；、」 (and Latin equivalents) lets the first
    short clause go to SoVITS immediately while the rest is synthesized in parallel.
    Fragments shorter than 2 characters are merged into the previous segment.
    """
    parts = [p.strip() for p in re.split(r"(?<=[。！？，；、!?;,\n])", text) if p.strip()]
    merged: list[str] = []
    for p in parts:
        if merged and len(p) < 2:
            merged[-1] += p
        else:
            merged.append(p)
    return merged


def speak_to_bytes(text: str) -> bytes:
    """Convert text to PCM audio bytes using the active TTS provider."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    pcm, _ = _synth(text)
    return pcm


def is_speaking() -> bool:
    """Check if 爱莉希雅 is currently speaking."""
    return _speaking.is_set()


def stop_speaking() -> None:
    """Interrupt current speech playback — instant."""
    _interrupt.set()
    # The queue player writes into the reused output stream; flushing it is what
    # makes the stop instant (sd.stop() alone leaves the queued buffer playing out).
    if _out_stream is not None:
        try:
            _out_stream.stop()
        except Exception:
            pass
    sd.stop()
    _speaking.clear()


def _wait_or_interrupt() -> bool:
    """Poll until audio finishes or interrupt is set. Returns True if interrupted."""
    while sd.get_stream() and sd.get_stream().active:
        if _interrupt.is_set():
            sd.stop()
            return True
        _interrupt.wait(0.05)  # 50ms poll
    return _interrupt.is_set()


def _resolve_ack_dir() -> Path:
    """tts.ack_dir from config, resolved against the repo root."""
    raw = _tts_cfg().get("ack_dir", "jarvis/data/ack")
    p = Path(raw)
    return p if p.is_absolute() else (_CONFIG_PATH.parent / p)


# Pre-loaded wake-ack audio, kept in memory as float32 PCM. Decoding a wav on the
# fly (wave.open + readframes + numpy cast) is a few ms, but the real cost is
# sounddevice opening a fresh output stream on every sd.play() call — that is what
# made the wake answer feel slow. The stream is opened once and reused, and the
# clips are cached at startup, so the ack starts as soon as the bytes are written.
_ack_cache: list[tuple[np.ndarray, int]] = []
_ack_pos = 0
_out_stream = None


def preload_ack_audio() -> int:
    """Load every tts.ack_dir wav into RAM once (called at startup)."""
    global _ack_cache
    ack_dir = _resolve_ack_dir()
    wavs = sorted(ack_dir.glob("*.wav")) if ack_dir.is_dir() else []
    cache = []
    for p in wavs:
        try:
            with wave.open(str(p), "rb") as w:
                rate = w.getframerate()
                pcm = w.readframes(w.getnframes())
            if pcm:
                cache.append((np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32767, rate))
        except Exception as e:
            print(f"[TTS] ack preload skipped {p.name}: {e}")
    _ack_cache = cache
    print(f"[TTS] ack audio preloaded: {len(cache)} clips in memory")
    # Warm the output stream at startup too: opening it costs ~3.4 s (measured),
    # so paying that here keeps the *first* wake answer as fast as the rest.
    if cache:
        try:
            t_open = time.perf_counter()
            _output_stream(cache[0][1])
            print(f"[TTS] output stream warmed in {1000 * (time.perf_counter() - t_open):.0f} ms")
        except Exception as e:
            print(f"[TTS] output stream warm-up failed (first ack will be slow): {e}")
    return len(cache)


def _output_stream(rate: int):
    """One long-lived output stream, reopened only when the sample rate changes."""
    global _out_stream
    if _out_stream is not None:
        if int(_out_stream.samplerate) == rate:
            if not _out_stream.active:
                _out_stream.start()
            return _out_stream
        try:
            _out_stream.stop()
            _out_stream.close()
        except Exception:
            pass
        _out_stream = None
    # No `latency="small"`: this sounddevice build wants a numeric blocksize
    # (frames), so a string raises TypeError: must be real number, not str.
    # The speedup comes from cached PCM + one reused stream, not a tiny buffer.
    _out_stream = sd.OutputStream(samplerate=rate, channels=1, dtype="float32")
    _out_stream.start()
    return _out_stream


def play_ack_wav() -> None:
    """T8: play a pre-synthesized wake-ack wav picked at random from tts.ack_dir.

    Cached PCM + reused output stream — no live TTS round-trip and no stream
    startup, so the "I'm listening" answer is near-instant. Falls back to live
    synthesis only when the cache/directory is empty. Interruptible via stop_speaking().
    """
    global _ack_pos
    if not _ack_cache:
        preload_ack_audio()
    if not _ack_cache:
        print("[TTS] No pre-generated ack wavs — falling back to live TTS")
        speak("嗯？我在听。")
        return
    t0 = time.perf_counter()
    audio, rate = _ack_cache[_ack_pos % len(_ack_cache)]
    _ack_pos += 1
    _interrupt.clear()
    _speaking.set()
    stream = None
    try:
        stream = _output_stream(rate)
        print(f"[TTS] ack stream ready in {1000 * (time.perf_counter() - t0):.0f} ms")
        chunk = max(1, int(rate * 0.1))
        for i in range(0, len(audio), chunk):
            if _interrupt.is_set():
                break
            stream.write(audio[i : i + chunk])
        print(f"[TTS] ack played ({len(audio) / rate:.2f} s), total {1000 * (time.perf_counter() - t0):.0f} ms")
    finally:
        if stream is not None and _interrupt.is_set():
            try:
                stream.stop()  # flush the queue so stop_speaking is instant
            except Exception:
                pass
        _speaking.clear()
        _interrupt.clear()


def _produce_segments(sentences: list[str], q: "queue.Queue") -> None:
    """Producer side of the TTS queue: synthesize segments in order and push PCM.

    The queue is bounded, so the producer runs **at most a few segments ahead** of
    playback — segment k+1 is being synthesized by SoVITS while segment k is already
    playing on the output stream. Bounded size keeps memory small (each 24 kHz int16
    segment is ~100 KB per second of speech) and keeps ordering strict: the consumer
    pops in the same order the producer pushed.
    """
    for s in sentences:
        if _interrupt.is_set():
            break
        try:
            pcm, rate = _synth(s)
        except Exception as e:
            print(f"[TTS] segment synth failed ({s[:12]!r}): {e}")
            break
        if pcm:
            q.put((pcm, rate))
    q.put(None)  # sentinel: producer finished


def speak_queued(text: str) -> None:
    """Speak text through the synthesis queue — the first clause sounds as soon as
    SoVITS returns it, the rest is synthesized ahead of playback. Interruptible via
    stop_speaking() (which flushes the reused output stream).
    """
    sentences = _split_sentences(text)
    if not sentences:
        return
    _interrupt.clear()
    _speaking.set()
    t0 = time.perf_counter()
    q = queue.Queue(maxsize=4)
    prod = threading.Thread(target=_produce_segments, args=(sentences, q), daemon=True)
    prod.start()
    first_ms = None
    played = 0.0
    interrupted = False
    last_rate = None
    try:
        while True:
            item = q.get()
            if item is None:
                break
            pcm, rate = item
            last_rate = rate
            if _interrupt.is_set():
                interrupted = True
                break
            audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32767
            if first_ms is None:
                first_ms = 1000 * (time.perf_counter() - t0)
            stream = _output_stream(rate)
            chunk = max(1, int(rate * 0.1))
            for i in range(0, len(audio), chunk):
                if _interrupt.is_set():
                    interrupted = True
                    break
                stream.write(audio[i : i + chunk])
            played += len(audio) / rate
            if interrupted:
                break
    finally:
        if _interrupt.is_set() and last_rate is not None:
            try:
                _output_stream(last_rate).stop()
            except Exception:
                pass
        _speaking.clear()
        _interrupt.clear()
        first = f"{first_ms:.0f} ms" if first_ms is not None else "n/a"
        print(
            f"[TTS] queued: {len(sentences)} segments, first sound {first}, "
            f"played {played:.2f} s, total {1000 * (time.perf_counter() - t0):.0f} ms"
            + (" (interrupted)" if interrupted else "")
        )


def speak(text: str) -> None:
    """Speak text aloud. Can be interrupted via stop_speaking()."""
    _interrupt.clear()
    pcm, rate = _synth(text)
    if not pcm:
        return
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32767
    _speaking.set()
    sd.play(audio, samplerate=rate)
    _wait_or_interrupt()
    _speaking.clear()


def speak_streamed(text: str) -> None:
    """Speak text sentence by sentence — starts playing before full generation is done.
    Can be interrupted mid-stream via stop_speaking()."""
    _interrupt.clear()
    sentences = _split_sentences(text)
    if not sentences:
        return

    if _active_provider() == "gptsovits":
        # Queue path (2026-11-11): segments go to SoVITS in order, segment k plays
        # as soon as it is ready while segment k+1 is being synthesized.
        speak_queued(text)
        return

    # Short text — just speak normally
    if len(sentences) == 1:
        speak(text)
        return

    pipeline = _get_pipeline()
    voice = _get_voice()
    cfg = _load_config()
    speed = cfg["tts"]["speed"]

    _speaking.set()
    try:
        for sentence in sentences:
            if _interrupt.is_set():
                break
            chunks = []
            for _, _, audio in pipeline(sentence, voice=voice, speed=speed):
                if _interrupt.is_set():
                    break
                if audio is not None:
                    chunks.append(audio)
            if not chunks or _interrupt.is_set():
                break
            combined = np.concatenate(chunks)
            sd.play(combined, samplerate=24000)
            if _wait_or_interrupt():
                break
    finally:
        sd.stop()  # ensure audio stops even if we break mid-play
        _speaking.clear()
        _interrupt.clear()
