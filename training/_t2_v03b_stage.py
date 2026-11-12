import os, sys, shutil
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
import numpy as np
from _t2_stream_features_v02 import (stream, clip_windows, load_wav,
    AudioFeatures, WARMUP, CHUNK, NFR, MAXW)

OWW = os.path.join(ROOT, "openWakeWord", "output")
V1 = os.path.join(OWW, "aili_xiya_v0.1")
V3 = os.path.join(OWW, "aili_xiya_v0.3")

# 1) stage remaining clean adversarial clips from v0.1 pool [950:2000]
v1_negs = sorted(f for f in os.listdir(os.path.join(V1, "negative_train")) if f.endswith(".wav"))
assert len(v1_negs) >= 2000, f"v0.1 neg pool {len(v1_negs)} < 2000"
sel = v1_negs[950:2000]
dst_dir = os.path.join(V3, "negative_train")
os.makedirs(dst_dir, exist_ok=True)
n_new = 0
for i, f in enumerate(sel):
    d = os.path.join(dst_dir, f"negadv_tr_{1000 + i:04d}.wav")
    if not (os.path.exists(d) and os.path.getsize(d) > 0):
        shutil.copy2(os.path.join(V1, "negative_train", f), d); n_new += 1
print(f"staged new negadv_tr clips: {n_new}", flush=True)

# 2) streaming features for the NEW clips only (index >= 1000)
neg_dir = os.path.join(V3, "negative_train")
files = sorted(f for f in os.listdir(neg_dir) if f.startswith("negadv_tr_") and int(f.split("_")[2][:4]) >= 1000)
print(f"new negadv_tr clips to feature: {len(files)}", flush=True)
assert len(files) == 1050, f"expected 1050 new clips, got {len(files)}"

base = np.load(os.path.join(V3, "negative_features_train.npy"))
print(f"base negative_features_train: {base.shape}", flush=True)
assert base.shape[0] == 33600, f"unexpected base rows {base.shape[0]}"

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
        print(f"[negadv_tr new] {i+1}/{len(files)} -> {len(rows)} rows", flush=True)

new = np.array(rows, dtype=np.float32)
print(f"new rows: {new.shape}, skipped={skipped}", flush=True)
out = np.concatenate([base, new], axis=0)
tmp = os.path.join(V3, "negative_features_train_new.npy")
np.save(tmp, out)
os.replace(tmp, os.path.join(V3, "negative_features_train.npy"))
print(f"final negative_features_train: {out.shape}", flush=True)
