"""Compare batch (embed_clips) vs streaming (predict-identical) features through the ONNX model."""
import wave
import numpy as np
import onnxruntime as ort
from openwakeword.utils import AudioFeatures

D = "openWakeWord/output/aili_xiya_v0.2"
m = ort.InferenceSession(D + "/aili_xiya_v0.2.onnx", providers=["CPUExecutionProvider"])
inp = m.get_inputs()[0].name

def score(x):
    return float(m.run(None, {inp: x[None,]})[0][0, 0])

def load_wav(p):
    with wave.open(p, "rb") as f:
        return np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)

pos_np = np.load(D + "/positive_features_test.npy").astype(np.float32)
neg_np = np.load(D + "/negative_features_test.npy").astype(np.float32)
print("saved pos row0:", pos_np[0].shape, "score=", score(pos_np[0]), flush=True)
print("saved neg row0:", neg_np[0].shape, "score=", score(neg_np[0]), flush=True)

for tag, path in (("pos", D + "/positive_test/pos_te_0000.wav"),
                 ("neg", D + "/negative_test/negx_te_000.wav")):
    data = load_wav(path)
    print(f"{tag} clip samples={data.shape[0]} ({data.shape[0]/16000:.2f}s)", flush=True)

    Fb = AudioFeatures(inference_framework="onnx", ncpu=4)
    bfeat = Fb.embed_clips(data[None,], batch_size=1)
    bs = score(bfeat[0][:24]) if bfeat.shape[0] >= 24 else float("nan")
    print(f"  batch: {bfeat.shape} score={bs:.4f}", flush=True)

    Fs = AudioFeatures(inference_framework="onnx", ncpu=4)
    padded = np.concatenate((np.zeros(16000, dtype=np.int16), data))
    frames = []
    for i in range(0, padded.shape[0], 1280):
        Fs(padded[i:i+1280])
        if len(Fs.feature_buffer) > len(frames):
            frames.append(Fs.feature_buffer[len(frames):len(Fs.feature_buffer)])
    allf = np.concatenate([np.asarray(f) for f in frames], axis=0)
    print(f"  streaming: {allf.shape} frames", flush=True)
    s_all = [score(allf[i:i+24]) for i in range(0, allf.shape[0]-23)]
    print(f"  streaming window scores: min={min(s_all):.4f} max={max(s_all):.4f}", flush=True)

    tail_b = bfeat[0][-5:]
    tail_s = allf[-5:]
    d = np.abs(tail_b - tail_s).max()
    print(f"  last-5 frames |batch - streaming| max diff = {d:.4f}", flush=True)
