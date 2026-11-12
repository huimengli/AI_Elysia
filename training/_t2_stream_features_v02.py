"""Recompute aili_xiya_v0.2 feature npys via the STREAMING pipeline that is
identical to openwakeword.Model.predict_clip (AudioFeatures(inference_framework=
"onnx") + 1 s zero warmup, 1280-sample chunks).

Why: v0.2 trained on batch embed_clips features (whole-clip melspec) while
verify/deployment scores via predict_clip streaming frames -> train/inference
feature mismatch + ~1150-epoch memorization => verify FAIL (HB-027).

Deployment scoring (model.py L287-302): after each 1280-sample chunk, the model
scores the LAST 24 frames of feature_buffer. Measured in this venv: ~10 feature
frames per 1280-sample chunk (24 frames ~= 190 ms receptive field), prefix
(random init + 1 s warmup) = 53 frames. Therefore the training distribution is:
  * one candidate window per chunk boundary (last-24 frames at that point);
  * pos clips: keep candidates with >= MIN_OVERLAP/24 frames inside the voiced
    region (RMS gate on raw clip, samples-per-frame measured per clip), cap
    MAXW by even spacing; fallback = single central candidate;
  * neg clips: all candidates, capped MAXW by even spacing (silence/noise/
    speech are all valid negatives);
  * val_fp.npy: re-streamed from the same seed-3 mixture recipe as
    _t2_make_val_fp_v02.py (~5 min background, chunks x0.3), last 120 frames.

Writes in place under openWakeWord/output/aili_xiya_v0.2/:
  positive_features_train.npy  positive_features_test.npy
  negative_features_train.npy  negative_features_test.npy  val_fp.npy

Run:  .venv\\Scripts\\python.exe _t2_stream_features_v02.py
"""
import os
import random
import sys
import time
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.2")
SR = 16000
CHUNK = 1280
WARMUP = 16000          # 1 s, matches predict_clip(padding=1)
NFR = 24                # model input frames per window
MIN_OVERLAP = 12        # pos windows need >=12/24 voiced frames
MARGIN = 3              # +- frame safety margin on the voiced region
MAXW = 12               # max kept windows per clip (evenly spaced)

# --- sandbox: no named pipes -> never let openwakeword spawn a ThreadPool ---
import openwakeword.utils as _u


class _SerialThreadPool:
    def __init__(self, *a, **k):
        pass

    def map(self, fn, it, chunksize=None):
        return [fn(x) for x in it]

    def close(self):
        pass

    def terminate(self):
        pass

    def join(self):
        pass


_u.ThreadPool = _SerialThreadPool

from openwakeword.utils import AudioFeatures  # noqa: E402


def load_wav(p):
    with wave.open(p, "rb") as f:
        assert f.getframerate() == SR and f.getsampwidth() == 2 and f.getnchannels() == 1, p
        return np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)


def stream(F, data):
    """Stream padded audio through F; return (all_frames, bounds) where
    all_frames includes the random-init + warmup prefix and bounds = frame
    count after each chunk that has >= NFR frames (the chunk boundaries at
    which Model.predict would score)."""
    F.reset()
    padded = np.concatenate((np.zeros(WARMUP, np.int16), data, np.zeros(WARMUP, np.int16)))
    parts = []
    bounds = []
    last_n = 0
    for i in range(0, padded.shape[0] - CHUNK, CHUNK):
        F(padded[i:i + CHUNK])
        n = F.feature_buffer.shape[0]
        if n > last_n:
            parts.append(F.feature_buffer[last_n:n].copy())
            last_n = n
        if n >= NFR:
            bounds.append(n)
    frames = np.concatenate(parts, axis=0).astype(np.float32) if parts else np.zeros((0, 96), np.float32)
    return frames, bounds


def measure_prefix(F):
    """Frames produced by the WARMUP zeros alone (random init + warmup)."""
    F.reset()
    last_n = 0
    for i in range(0, WARMUP - CHUNK, CHUNK):
        F(np.zeros(CHUNK, np.int16))
        n = F.feature_buffer.shape[0]
        if n > last_n:
            last_n = n
    return last_n


def voiced_range(data, spf, margin=MARGIN):
    """Voiced frame range of the clip in stream-frame index space.
    spf = samples per feature frame (measured per clip)."""
    nfr = data.shape[0] // CHUNK
    if nfr == 0:
        return None
    rms = np.array([np.sqrt(np.mean((data[i * CHUNK:(i + 1) * CHUNK].astype(np.float32)) ** 2))
                    for i in range(nfr)])
    if rms.max() <= 0:
        return None
    thr = max(0.05 * rms.max(), 1e-4)
    idx = np.where(rms > thr)[0]
    if len(idx) == 0:
        return None
    f0 = int((WARMUP + int(idx[0]) * CHUNK) / spf) - margin
    f1 = int((WARMUP + (int(idx[-1]) + 1) * CHUNK) / spf) + margin
    return max(f0, 0), f1


def _cap(even, n):
    if len(even) <= n:
        return even
    sel = np.unique(np.round(np.linspace(0, len(even) - 1, n)).astype(int))
    return [even[i] for i in sel]


def clip_windows(frames, vr, positive, bounds):
    """Chunk-boundary last-24-frame windows (deployment-consistent)."""
    M = frames.shape[0]
    cands = [b for b in bounds if NFR <= b <= M]
    if not cands:
        return []
    if not positive:
        return [frames[b - NFR:b] for b in _cap(cands, MAXW)]
    if vr is None:
        mid = min(cands, key=lambda b: abs(b - M // 2))
        return [frames[mid - NFR:mid]]
    f0, f1 = vr
    kept = [b for b in cands if min(b, f1) - max(b - NFR, f0) >= MIN_OVERLAP]
    if not kept:
        best = max(cands, key=lambda b: min(b, f1) - max(b - NFR, f0))
        if min(best, f1) - max(best - NFR, f0) > 0:
            kept = [best]
    return [frames[b - NFR:b] for b in _cap(kept, MAXW)]


def process_set(F, name, positive):
    d = os.path.join(D, name)
    files = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".wav"))
    rows, n_skipped = [], 0
    t0 = time.time()
    for k, p in enumerate(files):
        data = load_wav(p)
        frames, bounds = stream(F, data)
        M = frames.shape[0]
        spf = (WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = voiced_range(data, spf) if positive else None
        ws = clip_windows(frames, vr, positive, bounds)
        if not ws:
            n_skipped += 1
        rows.extend(ws)
        if (k + 1) % 200 == 0:
            el = time.time() - t0
            print(f"[{name}] {k + 1}/{len(files)} clips -> {len(rows)} rows "
                  f"({el:.0f}s, ETA {el / (k + 1) * (len(files) - k - 1):.0f}s)", flush=True)
    arr = np.stack(rows, axis=0).astype(np.float32) if rows else np.zeros((0, NFR, 96), np.float32)
    out = os.path.join(D, f"{name}_features_{'train' if 'train' in name else 'test'}.npy")
    np.save(out, arr)
    el = time.time() - t0
    print(f"[{name}] DONE: {len(files)} clips -> {arr.shape[0]} rows, skipped={n_skipped}, "
          f"{el:.0f}s -> {os.path.basename(out)}", flush=True)
    return arr


def make_val_fp(F):
    NOISE_DIR = os.path.join(ROOT, "openWakeWord", "background", "noise")
    SPEECH_DIR = os.path.join(ROOT, "openWakeWord", "background", "speech")
    files = sorted([os.path.join(NOISE_DIR, f) for f in os.listdir(NOISE_DIR)]
                   + [os.path.join(SPEECH_DIR, f) for f in os.listdir(SPEECH_DIR)])
    chunks = []
    total = 0
    rng = random.Random(3)
    target = 5 * 60 * SR
    while total < target:
        p = rng.choice(files)
        with wave.open(p, "rb") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        chunks.append(x * 0.3)
        total += len(x)
    audio = np.concatenate(chunks)[:target].astype(np.int16)
    F.reset()
    for i in range(0, audio.shape[0] - CHUNK, CHUNK):
        F(audio[i:i + CHUNK])
    buf = F.feature_buffer[-120:].astype(np.float32)
    out = os.path.join(D, "val_fp.npy")
    np.save(out, buf)
    print(f"[valfp] val_fp.npy saved: {buf.shape} -> {out}", flush=True)


if __name__ == "__main__":
    t_start = time.time()
    F = AudioFeatures(inference_framework="onnx", ncpu=1)
    prefix = measure_prefix(F)
    print(f"[init] prefix frames (random init + 1 s warmup): {prefix}", flush=True)

    for name, pos in (("positive_train", True), ("negative_train", False),
                      ("positive_test", True), ("negative_test", False)):
        process_set(F, name, pos)

    make_val_fp(F)
    print(f"[all] DONE in {time.time() - t_start:.0f}s", flush=True)
