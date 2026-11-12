import os, sys
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi")
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
from _t2_stream_features_v02 import (stream, measure_prefix, voiced_range,
    clip_windows, load_wav, AudioFeatures, WARMUP)
F = AudioFeatures(inference_framework="onnx", ncpu=1)
prefix = measure_prefix(F)
print("prefix:", prefix, flush=True)
D = r"C:\Users\楼听\Desktop\git\JarvisAi\openWakeWord\output\aili_xiya_v0.2"
for name in ("positive_train", "negative_train"):
    pos = name.startswith("positive")
    d = os.path.join(D, name)
    for f in sorted(os.listdir(d))[:5]:
        data = load_wav(os.path.join(d, f))
        frames, bounds = stream(F, data)
        M = frames.shape[0]
        spf = (WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = voiced_range(data, spf) if pos else None
        ws = clip_windows(frames, vr, pos, bounds)
        print(name, f[:40], "M=", M, "spf=%.1f" % spf, "bounds=", len(bounds),
              "vr=", vr, "win=", len(ws), flush=True)
