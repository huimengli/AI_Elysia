"""GSV-Elysia based sample generator with the piper-compatible interface.

openWakeWord's train.py does:
    sys.path.insert(0, config["piper_sample_generator_path"])
    from generate_samples import generate_samples
and calls (keyword style):
    generate_samples(text=..., max_samples=..., batch_size=...,
                     noise_scales=[0.98], noise_scale_ws=[0.98],
                     length_scales=[0.75, 1.0, 1.25],
                     output_dir=..., auto_reduce_batch_size=True,
                     file_names=[...])           # file_names optional
where text is a str (single phrase) or list[str] (phrases to interleave).

This implementation synthesizes each phrase with the local GPT-SoVITS 2.0
api_v2 endpoint (Elysia voice), resamples to 16 kHz mono, applies piper-style
length scaling + optional gaussian noise on top of a base prosody (speed)
variation, adds edge silence, and writes 16-bit WAV files.
"""
import io
import os
import random
import sys
import time
import uuid
import urllib.parse
import urllib.request
import wave

import numpy as np
from scipy.signal import resample_poly

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_URL = "http://127.0.0.1:9880/tts"
REF_AUDIO_PATH = r"F:\BaiduNetdiskDownload\爱莉希雅\【GPT-SoVITS 2.0】爱莉希雅\参考音频\【感动】欸嘿，大家笑一笑，好吗？.wav"
PROMPT_TEXT = "欸嘿，大家笑一笑，好吗？"
TARGET_SR = 16000


def synth(text: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
    """Synthesize text via GSV; returns (float32 mono samples, sample_rate)."""
    params = {
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": REF_AUDIO_PATH,
        "prompt_lang": "zh",
        "prompt_text": PROMPT_TEXT,
        "speed_factor": speed,
        "text_split_method": "cut5",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                data = r.read()
            break
        except Exception as e:  # noqa: BLE001 — transient GSV/transport errors
            last_err = e
            time.sleep(2.0 * (attempt + 1))
    else:
        raise RuntimeError(f"GSV synthesis failed after 3 attempts: {last_err}")
    with wave.open(io.BytesIO(data), "rb") as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    return x, rate


def _to_target_rate(x: np.ndarray, rate: int) -> np.ndarray:
    if rate == TARGET_SR:
        return x
    g = int(np.gcd(rate, TARGET_SR))
    return resample_poly(x, TARGET_SR // g, rate // g)


def _length_scale(x: np.ndarray, scale: float) -> np.ndarray:
    """Resample to len*scale (interpolation: length + slight pitch change)."""
    target = max(int(len(x) * scale), int(0.2 * TARGET_SR))
    if target == len(x):
        return x
    g = int(np.gcd(target, len(x)))
    return resample_poly(x, target // g, len(x) // g)


def _finalize(x: np.ndarray) -> np.ndarray:
    """Peak-normalize and pad short random silence at both edges."""
    peak = np.max(np.abs(x))
    if peak > 0:
        x = x * (0.9 / peak)
    pad_a = int(random.uniform(0.1, 0.4) * TARGET_SR)
    pad_b = int(random.uniform(0.1, 0.4) * TARGET_SR)
    return np.concatenate((np.zeros(pad_a, dtype=np.float32), x, np.zeros(pad_b, dtype=np.float32)))


def _save_wav(x: np.ndarray, path: str) -> None:
    xi = np.clip(x * 32768.0, -32768, 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TARGET_SR)
        w.writeframes(xi.tobytes())


def generate_samples(text, max_samples: int, batch_size: int, output_dir: str,
                     file_names: list[str] | None = None,
                     noise_scales=(1.0,), noise_scale_ws=(1.0,),
                     length_scales=(1.0,), auto_reduce_batch_size: bool = True) -> None:
    """Write up to max_samples 16 kHz mono WAV clips (piper-compatible).

    noise_scales/noise_scale_ws: per piper semantics — ws is the probability
    of adding gaussian white noise, scales*0.01 its amplitude.
    length_scales: random target length multipliers applied by interpolation.
    """
    if isinstance(text, str):
        phrases = [text]
    else:
        phrases = list(text)
    if file_names is None:
        file_names = [uuid.uuid4().hex + ".wav" for _ in range(int(max_samples))]
    n = min(int(max_samples), len(file_names))
    os.makedirs(output_dir, exist_ok=True)
    for i in range(n):
        target_path = os.path.join(output_dir, file_names[i])
        if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
            continue  # resumable: keep existing clip
        phrase = phrases[i % len(phrases)]
        speed = random.uniform(0.9, 1.1)
        x, rate = synth(phrase, speed=speed)
        x = _to_target_rate(x, rate)
        ls = length_scales[i % len(length_scales)]
        x = _length_scale(x, float(ls))
        ws = noise_scale_ws[i % len(noise_scale_ws)]
        if random.random() < float(ws):
            amp = float(noise_scales[i % len(noise_scales)]) * 0.01
            x = x + np.random.randn(len(x)).astype(np.float32) * amp
        x = _finalize(x)
        _save_wav(x, os.path.join(output_dir, file_names[i]))
        if (i + 1) % 25 == 0:
            print(f"[generate_samples] {i + 1}/{n} written -> {output_dir}", flush=True)
    print(f"[generate_samples] done: {n} clips in {output_dir}", flush=True)


if __name__ == "__main__":
    # Standalone smoke test: python generate_samples.py "爱莉希雅" 3 <outdir>
    phrase = sys.argv[1] if len(sys.argv) > 1 else "爱莉希雅"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    outdir = sys.argv[3] if len(sys.argv) > 3 else "."
    names = [f"smoke_{i}.wav" for i in range(count)]
    generate_samples(phrase, count, 1, outdir, names,
                     noise_scales=[0.98], noise_scale_ws=[0.5],
                     length_scales=[0.75, 1.0, 1.25])
