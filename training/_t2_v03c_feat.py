import os, sys
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
import numpy as np
from _t2_stream_features_v02 import (stream, clip_windows, load_wav,
    AudioFeatures, WARMUP, CHUNK, NFR, MAXW)

V3 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.3")
neg_dir = os.path.join(V3, "negative_train")
files = sorted(f for f in os.listdir(neg_dir) if (f.startswith("negx2_tr_") or f.startswith("noise2_tr_")))
print(f"new v0.3c clips: {len(files)}", flush=True)
assert len(files) == 950, f"expected 950 new clips, got {len(files)}"

base = np.load(os.path.join(V3, "negative_features_train.npy"))
print(f"base negative_features_train: {base.shape}", flush=True)
assert base.shape[0] == 46200, f"unexpected base rows {base.shape[0]}"

F = AudioFeatures(inference_framework="onnx", ncpu=1)
rows, skipped = [], 0
for i, f in enumerate(files):
    data = load_wav(os.path.join(neg_dir, f))
    frames, bounds = stream(F, data)
    ws = clip_windows(frames, None, False, bounds)
    if not ws:
        skipped += 1; continue
    rows.extend(ws)
    if (i + 1) % 100 == 0:
        print(f"[v03c] {i+1}/{len(files)} -> {len(rows)} rows", flush=True)

new = np.array(rows, dtype=np.float32)
print(f"new rows: {new.shape}, skipped={skipped}", flush=True)
out = np.concatenate([base, new], axis=0)
tmp = os.path.join(V3, "negative_features_train_new.npy")
np.save(tmp, out)
os.replace(tmp, os.path.join(V3, "negative_features_train.npy"))
print(f"final negative_features_train: {out.shape}", flush=True)
