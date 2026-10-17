from pathlib import Path
import io
import random
import re
import urllib.parse
import urllib.request
import wave
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
    """Split text into sentences for streaming TTS."""
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


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


def play_ack_wav() -> None:
    """T8: play a pre-synthesized wake-ack wav picked at random from tts.ack_dir.

    Local file playback — no live TTS round-trip, so the "I'm listening" ack is
    instant. Falls back to live synthesis when the directory is missing/empty.
    Interruptible via stop_speaking().
    """
    ack_dir = _resolve_ack_dir()
    wavs = sorted(ack_dir.glob("*.wav")) if ack_dir.is_dir() else []
    if not wavs:
        print("[TTS] No pre-generated ack wavs — falling back to live TTS")
        speak("嗯？我在听。")
        return
    pick = random.choice(wavs)
    with wave.open(str(pick), "rb") as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    if not pcm:
        speak("嗯？我在听。")
        return
    _interrupt.clear()
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32767
    _speaking.set()
    try:
        sd.play(audio, samplerate=rate)
        _wait_or_interrupt()
    finally:
        sd.stop()
        _speaking.clear()
        _interrupt.clear()


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
        # Per-sentence HTTP synthesis; each sentence plays as soon as it is ready.
        _speaking.set()
        try:
            for sentence in sentences:
                if _interrupt.is_set():
                    break
                pcm, rate = _gptsovits_synth(sentence)
                if not pcm or _interrupt.is_set():
                    break
                audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32767
                sd.play(audio, samplerate=rate)
                if _wait_or_interrupt():
                    break
        finally:
            sd.stop()  # ensure audio stops even if we break mid-play
            _speaking.clear()
            _interrupt.clear()
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
