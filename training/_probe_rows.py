"""Score saved feature rows across train/test pos/neg."""
import numpy as np
import onnxruntime as ort

D = "openWakeWord/output/aili_xiya_v0.2"
m = ort.InferenceSession(D + "/aili_xiya_v0.2.onnx", providers=["CPUExecutionProvider"])
inp = m.get_inputs()[0].name
idxs = [0, 5, 10, 25, 50, 100]

for name in ("positive_features_train", "negative_features_train", "positive_features_test", "negative_features_test"):
    a = np.load(D + "/" + name + ".npy").astype(np.float32)
    out = []
    for i in idxs:
        r = m.run(None, {inp: a[i:i+1]})
        out.append(float(r[0][0, 0]))
    print(name, "rows=", a.shape[0], "scores:", [f"{x:.4f}" for x in out], flush=True)
