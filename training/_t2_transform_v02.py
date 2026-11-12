"""v0.2 dataset assembly (local, no GSV needed).

Breaks the timbre shortcut: BOTH classes carry the same strong-transform
distribution, so only CONTENT can separate them.

Layout under openWakeWord/output/aili_xiya_v0.2/:
  positive_train  (2000) = 1000 clean Elysia (copied from v0.1) + 1000 strongly transformed
  positive_test   (400)  = clean Elysia (copied from v0.1)
  negative_train  (2000) = 1550 strongly-transformed other-speech (from neg_src) + 450 noise/silence
  negative_test   (400)  = 150 clean adversarial Elysia (copied from v0.1 negative_train)
                           + 150 strongly-transformed other-speech (neg_src holdout)
                           + 100 noise/silence

Strong transform: pitch +/-4..10 st, time-stretch 0.78..1.28 (length restored),
random low/high/bandpass (2nd-order butter, p=0.65), colored noise SNR 8..20 dB
(p=0.5), peak-norm 0.9. Resumable; waits for neg_src files to appear.
"""
import os
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import math
import numpy as np
import scipy.signal
import wave

ROOT = Path(__file__).resolve().parent
V01 = ROOT / "openWakeWord" / "output" / "aili_xiya_v0.1"
V02 = ROOT / "openWakeWord" / "output" / "aili_xiya_v0.2"
NEG_SRC = V02 / "neg_src"
SR = 16000

N_POS_CLEAN, N_POS_TRANS = 1000, 1000
N_NEG_TRAIN, N_NOISE_TRAIN = 1550, 450
N_NEG_TEST, N_NOISE_TEST = 150, 100


def _load_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return x


def _save_wav(x: np.ndarray, path: Path) -> None:
    xi = np.clip(x * 32768.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(xi.tobytes())


def _peak_norm(x: np.ndarray, peak: float = 0.9) -> np.ndarray:
    p = float(np.max(np.abs(x))) if x.size else 0.0
    return x * (peak / p) if p > 1e-9 else x


def _pink_noise(n: int, rng: random.Random) -> np.ndarray:
    # FFT-based 1/f pink noise: stable for any length. The classic Kellet IIR has a
    # pole at |z|~1.0074 -> float64 overflow beyond ~2e5 samples (v0.2 run, HB-023).
    white = np.random.default_rng(int(rng.random() * 1e9)).standard_normal(n).astype(np.float64)
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, d=1.0 / SR)
    freqs[0] = 1.0
    out = np.fft.irfft(spec / np.sqrt(freqs), n=n)
    rms = float(np.sqrt(np.mean(out ** 2))) or 1.0
    return (out / rms * 0.5).astype(np.float32)


def _resample_len(x: np.ndarray, target_len: int) -> np.ndarray:
    if target_len == len(x):
        return x
    g = math.gcd(target_len, len(x))
    return scipy.signal.resample_poly(x, target_len // g, len(x) // g).astype(np.float32)


def strong_transform(x: np.ndarray, seed: int) -> np.ndarray:
    """Resample-based timbre perturbation (scipy-only): pitch shift by
    +/-4..10 semitones, time smear 0.78..1.28, then restore original length."""
    rng = random.Random(seed)
    orig_len = len(x)
    st = rng.choice([-1, 1]) * rng.uniform(4.0, 10.0)
    r_pitch = 2.0 ** (st / 12.0)
    y = _resample_len(x, max(int(len(x) / r_pitch), 16))
    y = _resample_len(y, orig_len)
    f = rng.uniform(0.78, 1.28)
    y = _resample_len(y, max(int(orig_len / f), 16))
    y = _resample_len(y, orig_len)
    if rng.random() < 0.65:
        kind = rng.choice(["lowpass", "highpass", "bandpass"])
        if kind == "lowpass":
            sos = scipy.signal.butter(2, float(rng.uniform(1200, 4500)), btype="lowpass", fs=SR, output="sos")
        elif kind == "highpass":
            sos = scipy.signal.butter(2, float(rng.uniform(250, 1200)), btype="highpass", fs=SR, output="sos")
        else:
            lo, hi = sorted((float(rng.uniform(400, 2000)), float(rng.uniform(2500, 6000))))
            sos = scipy.signal.butter(2, [lo, hi], btype="bandpass", fs=SR, output="sos")
        y = scipy.signal.sosfilt(sos, y).astype(np.float32)
    if rng.random() < 0.5:
        snr_db = float(rng.uniform(8, 20))
        nrng = np.random.default_rng(seed + 1)
        white = nrng.standard_normal(len(y))
        noise = _pink_noise(len(y), rng) if rng.random() < 0.5 else white
        noise = np.asarray(noise, dtype=np.float32)
        rms = float(np.sqrt(np.mean(y ** 2))) or 1e-9
        y = y + noise * rms * 10.0 ** (-snr_db / 20.0)
    return _peak_norm(y)


def make_noise_silence(seed: int, n_samples: int) -> np.ndarray:
    rng = random.Random(seed)
    dur = rng.uniform(0.8, 3.0)
    x = np.zeros(n_samples, dtype=np.float32)
    kind = rng.choices(["silence", "white", "brown", "pink"], weights=[35, 35, 20, 10])[0]
    if kind != "silence":
        white = np.random.default_rng(seed + 1).standard_normal(n_samples).astype(np.float32)
        if kind == "white":
            x = white
        elif kind == "brown":
            x = np.cumsum(white.astype(np.float64))
            x -= x.mean()
        else:
            x = _pink_noise(n_samples, rng)
        rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) or 1.0
        target_peak = 10.0 ** (-rng.uniform(18, 6) / 20.0)  # -18dB .. -6dB
        x = x / rms * (target_peak * 1.414)
    pad = int(rng.uniform(0.1, 0.4) * SR)
    return np.concatenate((np.zeros(pad), x, np.zeros(pad))).astype(np.float32)


def _one(src: Path, dst: Path, seed: int):
    if dst.exists() and dst.stat().st_size > 0:
        return "skip"
    x = _load_wav(src)
    y = strong_transform(x, seed)
    dst.parent.mkdir(parents=True, exist_ok=True)
    _save_wav(y, dst)
    return "ok"


def main() -> None:
    workers = max(1, min(8, os.cpu_count() or 4))
    for d in ("positive_train", "positive_test", "negative_train", "negative_test"):
        (V02 / d).mkdir(parents=True, exist_ok=True)

    # --- positives: clean copies + strong transforms of half the v0.1 set ---
    pos_tr = sorted((V01 / "positive_train").glob("*.wav"))
    assert len(pos_tr) >= 2000, f"v0.1 positive_train has {len(pos_tr)} clips"
    clean_src = pos_tr[1000:2000]
    trans_src = pos_tr[0:1000]
    tasks = []
    for i, src in enumerate(clean_src):
        dst = V02 / "positive_train" / f"pos_tr_{i:04d}.wav"
        if not (dst.exists() and dst.stat().st_size > 0):
            dst.parent.mkdir(parents=True, exist_ok=True)
            _save_wav(_load_wav(src), dst)
    for i, src in enumerate(trans_src):
        tasks.append((src, V02 / "positive_train" / f"posx_tr_{i:04d}.wav", 90000 + i))
    pos_te = sorted((V01 / "positive_test").glob("*.wav"))
    for i, src in enumerate(pos_te):
        dst = V02 / "positive_test" / f"pos_te_{i:04d}.wav"
        if not (dst.exists() and dst.stat().st_size > 0):
            _save_wav(_load_wav(src), dst)
    print(f"[v02] positives staged: {len(clean_src)} clean + {len(trans_src)} to transform; "
          f"test {len(pos_te)} copied", flush=True)

    # --- noise / silence ---
    for i in range(N_NOISE_TRAIN):
        dst = V02 / "negative_train" / f"noise_tr_{i:03d}.wav"
        if not (dst.exists() and dst.stat().st_size > 0):
            _save_wav(make_noise_silence(70000 + i, int(random.Random(70001 + i).uniform(0.8, 3.0) * SR)), dst)
    for i in range(N_NOISE_TEST):
        dst = V02 / "negative_test" / f"noise_te_{i:03d}.wav"
        if not (dst.exists() and dst.stat().st_size > 0):
            _save_wav(make_noise_silence(80000 + i, int(random.Random(80001 + i).uniform(0.8, 3.0) * SR)), dst)

    # --- clean adversarial holdout for negative_test (v0.1 negatives contain the phrase) ---
    neg_tr_v01 = sorted((V01 / "negative_train").glob("*.wav"))
    adv = neg_tr_v01[0:150]
    for i, src in enumerate(adv):
        dst = V02 / "negative_test" / f"negadv_te_{i:03d}.wav"
        if not (dst.exists() and dst.stat().st_size > 0):
            _save_wav(_load_wav(src), dst)
    print(f"[v02] noise/silence {N_NOISE_TRAIN}/{N_NOISE_TEST} + adversarial holdout {len(adv)} done", flush=True)

    # --- sequential transforms (sandbox blocks multiprocessing pipes):
    #     positives first, then negatives as neg_src arrives ---
    import time
    for i, (s, d, sd) in enumerate(tasks):
        _one(s, d, sd)
        if i % 100 == 0:
            print(f"[v02] pos transforms {i}/{len(tasks)}", flush=True)

    def _neg_dst(idx: int) -> Path:
        return (V02 / "negative_train" / f"negx_tr_{idx:04d}.wav") if idx < N_NEG_TRAIN             else (V02 / "negative_test" / f"negx_te_{idx - N_NEG_TRAIN:03d}.wav")

    idx = 0
    while idx < 1700:
        src = NEG_SRC / f"neg_src_{idx:04d}.wav"
        if src.exists() and src.stat().st_size > 0:
            _one(src, _neg_dst(idx), 50000 + idx)
            idx += 1
            if idx % 100 == 0:
                print(f"[v02] neg transforms {idx}/1700", flush=True)
        else:
            time.sleep(30)

    # final counts
    for d in ("positive_train", "positive_test", "negative_train", "negative_test"):
        n = len(list((V02 / d).glob("*.wav")))
        print(f"[v02] {d}: {n} clips", flush=True)


if __name__ == "__main__":
    main()
