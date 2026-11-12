import os, sys
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
import numpy as np
from _t2_stream_features_v02 import (stream, clip_windows, load_wav,
    AudioFeatures, WARMUP, CHUNK, NFR, MAXW)

OWW = os.path.join(ROOT, "openWakeWord", "output")
V2 = os.path.join(OWW, "aili_xiya_v0.2")
V3 = os.path.join(OWW, "aili_xiya_v0.3")

# 1) copy existing feature npys from v0.2 (already validated streaming-consistent)
for name in ("positive_features_train.npy", "negative_features_train.npy",
             "positive_test_features_test.npy", "negative_test_features_test.npy",
             "val_fp.npy"):
    s, d = os.path.join(V2, name), os.path.join(V3, name)
    if not (os.path.exists(d) and os.path.getsize(d) > 0):
        import shutil; shutil.copy2(s, d)
        print(f"copied {name} <- v0.2", flush=True)

base = np.load(os.path.join(V3, "negative_features_train.npy"))
print(f"base negative_features_train: {base.shape}", flush=True)

# 2) streaming features for the 800 new clean adversarial clips
neg_dir = os.path.join(V3, "negative_train")
files = sorted(f for f in os.listdir(neg_dir) if f.startswith("negadv_tr_"))
print(f"negadv_tr clips: {len(files)}", flush=True)
assert len(files) == 800

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
        print(f"[negadv_tr] {i+1}/{len(files)} -> {len(rows)} rows", flush=True)

new = np.array(rows, dtype=np.float32)
print(f"new rows: {new.shape}, skipped={skipped}", flush=True)
out = np.concatenate([base, new], axis=0)
tmp = os.path.join(V3, "negative_features_train.npy.tmp")
np.save(tmp, out)
os.replace(tmp, os.path.join(V3, "negative_features_train.npy"))
print(f"final negative_features_train: {out.shape}", flush=True)
