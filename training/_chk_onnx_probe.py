import traceback, numpy as np
out = open(r"C:\Users\楼听\Desktop\git\JarvisAi\_chk_onnx_probe_out.txt", "w", encoding="utf-8")
out.write("START\n"); out.flush()
try:
    import onnxruntime as ort
    base = r"C:\Users\楼听\Desktop\git\JarvisAi\openWakeWord\output\aili_xiya_v0.1"
    sess = ort.InferenceSession(base + "\\" + "aili_xiya_v0.1.onnx", providers=["CPUExecutionProvider"])
    inp_name = sess.get_inputs()[0].name
    def P(s): out.write(s+"\n"); out.flush()
    P(f"input name={inp_name} shape={sess.get_inputs()[0].shape}")
    p = np.load(base + "\\" + "positive_features_train.npy", mmap_mode="r").astype(np.float32)
    n = np.load(base + "\\" + "negative_features_train.npy", mmap_mode="r").astype(np.float32)
    def score(win):
        return float(sess.run(None, {inp_name: win[None].astype(np.float32)})[0].squeeze())
    P(f"zeros(27x96)      -> {score(np.zeros((27,96),np.float32)):.6f}")
    P(f"rand(27x96)       -> {score(np.random.RandomState(0).randn(27,96)):.6f}")
    P(f"pos[0] full clip  -> {score(p[0]):.6f}")
    P(f"neg[0] full clip  -> {score(n[0]):.6f}")
    def maxwin(a):
        best = -1.0
        for i in range(0, a.shape[0]-27+1):
            v = score(a[i:i+27])
            if v > best: best = v
        return best
    P(f"pos[0] max over 27-frame windows -> {maxwin(p[0]):.6f}")
    P(f"neg[0] max over 27-frame windows -> {maxwin(n[0]):.6f}")
    for m in [0.1, 1.0, 10.0]:
        P(f"pos[0]*{m} full clip -> {score(p[0]*m):.6f}")
    # distribution over all test clips (25 each) to see spread
    import random; random.seed(1)
    pt = np.load(base + "\\" + "positive_features_test.npy", mmap_mode="r").astype(np.float32)
    nt = np.load(base + "\\" + "negative_features_test.npy", mmap_mode="r").astype(np.float32)
    pv = [score(pt[random.randrange(pt.shape[0])]) for _ in range(25)]
    nv = [score(nt[random.randrange(nt.shape[0])]) for _ in range(25)]
    P(f"pos test 25 samples: min={min(pv):.4f} max={max(pv):.4f}")
    P(f"neg test 25 samples: min={min(nv):.4f} max={max(nv):.4f}")
    out.write("DONE\n")
except Exception:
    out.write("EXCEPTION:\n"); out.write(traceback.format_exc()); out.flush()
out.close()
