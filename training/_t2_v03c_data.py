"""v0.3c data extension (resumable):
1) synthesize 500 NEW Elysia sentences -> neg_src_1700..2199 (same pipeline as _t2_synth_neg.py)
2) strong-transform each -> v0.3/negative_train/negx2_tr_{i:04d}.wav (seed 60000+i)
3) 450 new noise/silence -> v0.3/negative_train/noise2_tr_{i:03d}.wav (seed 71000+i)
"""
import os, sys, random
from pathlib import Path
ROOT = Path(r"C:\Users\楼听\Desktop\git\JarvisAi")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
sys.path.insert(0, str(ROOT / "openWakeWord"))
import numpy as np
from _t2_synth_neg import make_texts, synth, _to_target_rate, _length_scale, _finalize  # seeds random=42 on import
from _t2_transform_v02 import strong_transform, make_noise_silence, _load_wav, _save_wav, SR

NEG_SRC = ROOT / "openWakeWord" / "output" / "aili_xiya_v0.2" / "neg_src"
V3_NEG = ROOT / "openWakeWord" / "output" / "aili_xiya_v0.3" / "negative_train"
V3_NEG.mkdir(parents=True, exist_ok=True)
NEG_SRC.mkdir(parents=True, exist_ok=True)

# wait for GSV :9880 (any HTTP response = ready, incl. 404; no /version endpoint)
import urllib.request, urllib.error, time
for _ in range(240):
    try:
        urllib.request.urlopen("http://127.0.0.1:9880/", timeout=5)
        print("[ready] GSV :9880 up", flush=True); break
    except urllib.error.HTTPError:
        print("[ready] GSV :9880 up (HTTP response)", flush=True); break
    except Exception as ex:
        print(f"[wait] GSV not ready: {type(ex).__name__}", flush=True); time.sleep(10)
else:
    raise SystemExit("GSV :9880 never became ready")

N = 500
texts = make_texts(1700 + N)
assert len(texts) == 1700 + N
length_scales = [0.75, 1.0, 1.25]

# 1) synthesize missing neg_src clips (indices 1700..2199)
for i in range(N):
    idx = 1700 + i
    path = NEG_SRC / f"neg_src_{idx:04d}.wav"
    if not (path.exists() and path.stat().st_size > 0):
        x, rate = synth(texts[idx], speed=random.uniform(0.9, 1.1))
        x = _to_target_rate(x, rate)
        x = _length_scale(x, length_scales[idx % len(length_scales)])
        if random.random() < 0.5:
            x = x + (np.random.randn(len(x)).astype("float32") * (0.98 * 0.01))
        x = _finalize(x)
        _save_wav(x, str(path))
    if (i + 1) % 50 == 0:
        print(f"[synth] {i+1}/{N}", flush=True)
print("[synth] done", flush=True)

# 2) strong transform -> negx2_tr (new same-voice non-wake content)
done = 0
for i in range(N):
    idx = 1700 + i
    src = NEG_SRC / f"neg_src_{idx:04d}.wav"
    dst = V3_NEG / f"negx2_tr_{i:04d}.wav"
    if not (dst.exists() and dst.stat().st_size > 0):
        x = _load_wav(src)
        y = strong_transform(x, 60000 + i)
        _save_wav(y, dst)
        done += 1
print(f"[transform] {done} new negx2_tr clips", flush=True)

# 3) 450 new noise/silence (seed block 71000+, disjoint from 70000/80000)
done = 0
for i in range(450):
    dst = V3_NEG / f"noise2_tr_{i:03d}.wav"
    if not (dst.exists() and dst.stat().st_size > 0):
        _save_wav(make_noise_silence(71000 + i, int(random.Random(71001 + i).uniform(0.8, 3.0) * SR)), dst)
        done += 1
print(f"[noise] {done} new noise2_tr clips", flush=True)

print("v0.3c data ready:", sum(1 for f in os.listdir(V3_NEG) if f.endswith(".wav")), "total neg clips", flush=True)
