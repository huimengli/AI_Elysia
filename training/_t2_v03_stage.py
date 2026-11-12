import os, shutil
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
OWW = os.path.join(ROOT, "openWakeWord", "output")
V2 = os.path.join(OWW, "aili_xiya_v0.2")
V1 = os.path.join(OWW, "aili_xiya_v0.1")
V3 = os.path.join(OWW, "aili_xiya_v0.3")

def copy_dir(src_d, dst_d, pattern=None):
    os.makedirs(dst_d, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(src_d)):
        if not f.endswith(".wav"): continue
        if pattern and not any(f.startswith(p) for p in pattern): continue
        s = os.path.join(src_d, f); d = os.path.join(dst_d, f)
        if not (os.path.exists(d) and os.path.getsize(d) > 0):
            shutil.copy2(s, d); n += 1
    return n

counts = {}
counts["pos_train"] = copy_dir(os.path.join(V2, "positive_train"), os.path.join(V3, "positive_train"))
counts["pos_test"] = copy_dir(os.path.join(V2, "positive_test"), os.path.join(V3, "positive_test"))
counts["negx_tr"] = copy_dir(os.path.join(V2, "negative_train"), os.path.join(V3, "negative_train"), ("negx_tr", "noise_tr"))
counts["neg_te"] = copy_dir(os.path.join(V2, "negative_test"), os.path.join(V3, "negative_test"))

# clean adversarial train clips from v0.1 pool [150:950] (disjoint from test holdout [0:150])
v1_negs = sorted(f for f in os.listdir(os.path.join(V1, "negative_train")) if f.endswith(".wav"))
assert len(v1_negs) >= 950, f"v0.1 neg pool {len(v1_negs)} < 950"
sel = v1_negs[150:950]
dst_dir = os.path.join(V3, "negative_train")
os.makedirs(dst_dir, exist_ok=True)
n_new = 0
for i, f in enumerate(sel):
    d = os.path.join(dst_dir, f"negadv_tr_{i:04d}.wav")
    if not (os.path.exists(d) and os.path.getsize(d) > 0):
        shutil.copy2(os.path.join(V1, "negative_train", f), d); n_new += 1
counts["negadv_tr(new)"] = n_new

for k, v in counts.items(): print(f"{k}: {v}", flush=True)
total_neg = len([f for f in os.listdir(dst_dir) if f.endswith(".wav")])
print(f"negative_train total: {total_neg}", flush=True)
