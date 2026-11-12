"""Generate val_fp.npy for aili_xiya_v0.2 (same recipe as openWakeWord/_make_background.py
make_fp_validation): ~5 min background mix from background/noise + background/speech,
AudioFeatures feature buffer saved as float32 npy.
"""
import os
import random
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
OWW = os.path.join(ROOT, "openWakeWord")
NOISE_DIR = os.path.join(OWW, "background", "noise")
SPEECH_DIR = os.path.join(OWW, "background", "speech")
FP_DIR = os.path.join(OWW, "output", "aili_xiya_v0.2")
SR = 16000


def make_fp_validation() -> None:
    os.makedirs(FP_DIR, exist_ok=True)
    files = sorted(
        [os.path.join(NOISE_DIR, f) for f in os.listdir(NOISE_DIR)]
        + [os.path.join(SPEECH_DIR, f) for f in os.listdir(SPEECH_DIR)]
    )
    print(f"[valfp] source files: {len(files)}", flush=True)
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
    audio = np.concatenate(chunks)[:target]

    from openwakeword.utils import AudioFeatures
    feat = AudioFeatures(ncpu=4, device="cpu")
    feat(audio)
    buf = np.asarray(feat.feature_buffer, dtype=np.float32)
    out = os.path.join(FP_DIR, "val_fp.npy")
    np.save(out, buf)
    print(f"[valfp] val_fp.npy saved: {buf.shape} -> {out}", flush=True)


if __name__ == "__main__":
    make_fp_validation()
    print("[valfp] DONE", flush=True)
