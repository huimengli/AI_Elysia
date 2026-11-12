import os, sys
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
import numpy as np
import onnxruntime as ort
from _t2_stream_features_v02 import (stream, clip_windows, load_wav,
    AudioFeatures, voiced_range, WARMUP)

D = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.2")
onnx_path = os.path.join(D, "aili_xiya_v0.2.onnx")
# external data? check for .onnx.data
if not os.path.exists(onnx_path + ".data"):
    pass
sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
in_name = sess.get_inputs()[0].name
print("input:", in_name, sess.get_inputs()[0].shape, flush=True)

def score(x):
    return float(sess.run(None, {in_name: x[None]} )[0][0])

pos_tr = np.load(os.path.join(D, "positive_features_train.npy"))
neg_tr = np.load(os.path.join(D, "negative_features_train.npy"))
print("train rows:", pos_tr.shape, neg_tr.shape, flush=True)
for i in (0, 100, 500, 1900):
    print(f"pos_train[{i}] = {score(pos_tr[i]):.4f}", flush=True)
for i in (0, 100, 500, 1900):
    print(f"neg_train[{i}] = {score(neg_tr[i]):.4f}", flush=True)

# pure silence window via streaming 1 s zeros
F = AudioFeatures(inference_framework="onnx", ncpu=1)
frames, bounds = stream(F, np.zeros(16000, np.int16))
sil = frames[-24:]
print(f"silence window = {score(sil):.4f}", flush=True)

# streaming windows from test clips (max over chunk-boundary candidates)
for cls in ("negx_te", "negadv_te", "pos_te"):
    d = os.path.join(D, "negative_test" if "neg" in cls else "positive_test")
    files = sorted(f for f in os.listdir(d) if f.startswith(cls + "_"))[:5]
    for f in files:
        data = load_wav(os.path.join(d, f))
        frames, bounds = stream(F, data)
        M = frames.shape[0]
        spf = (WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = voiced_range(data, spf) if "pos" in cls else None
        ws = clip_windows(frames, vr, "pos" in cls, bounds)
        s = max(score(w) for w in ws) if ws else -1.0
        print(f"{f[:30]} max-boundary-window = {s:.4f} (nwin={len(ws)})", flush=True)
