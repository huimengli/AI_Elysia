import traceback, sys
out = open(r"C:\Users\楼听\Desktop\git\JarvisAi\_chk_feat_stats_out.txt", "w", encoding="utf-8")
out.write("START\n"); out.flush()
try:
    import numpy as np, random
    base = r"C:\Users\楼听\Desktop\git\JarvisAi\openWakeWord\output\aili_xiya_v0.1"
    def P(*a):
        out.write(" ".join(map(str,a)) + "\n"); out.flush()
    files = ["positive_features_train.npy","negative_features_train.npy","positive_features_test.npy","negative_features_test.npy","val_fp.npy"]
    for f in files:
        a = np.load(base + "\\" + f, mmap_mode="r")
        arr = np.asarray(a)
        P(f, "shape=", arr.shape, "dtype=", arr.dtype)
        P("  mean=", round(float(arr.mean()),6), "std=", round(float(arr.std()),6), "min=", round(float(arr.min()),4), "max=", round(float(arr.max()),4))
    p = np.asarray(np.load(base + "\\" + "positive_features_train.npy", mmap_mode="r"))
    n = np.asarray(np.load(base + "\\" + "negative_features_train.npy", mmap_mode="r"))
    for i in [0, 100, 500]:
        P(f"row{i}: pos norm={float(np.linalg.norm(p[i])):.4f} neg norm={float(np.linalg.norm(n[i])):.4f}")
    random.seed(7)
    def cos(a,b):
        a=a.flatten(); b=b.flatten()
        return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
    spn = sum(cos(p[random.randrange(p.shape[0])], n[random.randrange(n.shape[0])]) for _ in range(20))/20
    spp = sum(cos(p[random.randrange(p.shape[0])], p[random.randrange(p.shape[0])]) for _ in range(20))/20
    snn = sum(cos(n[random.randrange(n.shape[0])], n[random.randrange(n.shape[0])]) for _ in range(20))/20
    P(f"cosine sim pos-vs-neg={spn:.4f}  pos-vs-pos={spp:.4f}  neg-vs-neg={snn:.4f}")
    out.write("DONE\n")
except Exception:
    out.write("EXCEPTION:\n"); out.write(traceback.format_exc()); out.flush()
out.close()
