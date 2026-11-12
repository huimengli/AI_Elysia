"""Probe raw outputs of aili_xiya_v0.2.onnx on sample pos/neg features."""
import numpy as np
import onnxruntime as ort

D = "openWakeWord/output/aili_xiya_v0.2"
m = ort.InferenceSession(D + "/aili_xiya_v0.2.onnx", providers=["CPUExecutionProvider"])
inp = m.get_inputs()[0]
print("input:", inp.name, inp.shape, flush=True)
print("outputs:", [(o.name, o.shape) for o in m.get_outputs()], flush=True)

pos = np.load(D + "/positive_features_train.npy").astype(np.float32)
neg = np.load(D + "/negative_features_train.npy").astype(np.float32)
print("pos feat:", pos.shape, "neg feat:", neg.shape, flush=True)

for name, arr in (("pos", pos[:8]), ("neg", neg[:8])):
    outs = []
    for i in range(arr.shape[0]):
        r = m.run(None, {inp.name: arr[i:i+1]})
        v = np.asarray(r[0]).flatten()
        outs.append(v)
    a = np.stack(outs)
    print(name, "out min/max/mean:", a.min(), a.max(), a.mean(), flush=True)
    for i in range(a.shape[0]):
        print(" ", name, i, np.round(a[i], 4), flush=True)
