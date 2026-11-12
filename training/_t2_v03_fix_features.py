import os, shutil
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
OWW = os.path.join(ROOT, "openWakeWord", "output")
V2 = os.path.join(OWW, "aili_xiya_v0.2")
V3 = os.path.join(OWW, "aili_xiya_v0.3")
import numpy as np

# 1) quarantine stale corrupt npys in v0.2 (wrong-named partial files that shadowed the real ones)
stale_dir = os.path.join(V2, "_stale_npy")
os.makedirs(stale_dir, exist_ok=True)
for name in ("positive_features_train.npy", "negative_features_train.npy",
             "positive_features_test.npy", "negative_features_test.npy"):
    s = os.path.join(V2, name)
    if os.path.exists(s):
        shutil.move(s, os.path.join(stale_dir, name))
        print(f"quarantined v0.2/{name}", flush=True)

# 2) rebuild v0.3 train features from the correct 24k-row files
pos = np.load(os.path.join(V2, "positive_train_features_train.npy"))
print("v0.2 positive_train_features_train:", pos.shape, flush=True)
np.save(os.path.join(V3, "positive_features_train.npy"), pos)

neg_base = np.load(os.path.join(V2, "negative_train_features_train.npy"))
print("v0.2 negative_train_features_train:", neg_base.shape, flush=True)
tmp = np.load(os.path.join(V3, "negative_features_train.npy.tmp.npy"))
print("v0.3 tmp (corrupt base + new):", tmp.shape, flush=True)
new_rows = tmp[2000:]  # first 2000 rows were the corrupt stale base
assert new_rows.shape == (9600, 24, 96), new_rows.shape
neg_final = np.concatenate([neg_base, new_rows], axis=0)
tmpf = os.path.join(V3, "negative_features_train_build.npy")
np.save(tmpf, neg_final)
os.replace(tmpf, os.path.join(V3, "negative_features_train.npy"))
os.remove(os.path.join(V3, "negative_features_train.npy.tmp.npy"))
print("v0.3 negative_features_train final:", neg_final.shape, flush=True)

for name in ("positive_features_train.npy", "negative_features_train.npy",
             "positive_test_features_test.npy", "negative_test_features_test.npy", "val_fp.npy"):
    p = os.path.join(V3, name)
    print(f"v0.3 {name}: {np.load(p).shape}", flush=True)
