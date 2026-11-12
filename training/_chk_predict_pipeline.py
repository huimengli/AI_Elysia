import traceback, numpy as np, glob
out = open(r"C:\Users\楼听\Desktop\git\JarvisAi\_chk_predict_pipeline_out.txt", "w", encoding="utf-8")
def P(s): out.write(str(s)+"\n"); out.flush()
P("START")
try:
    import openwakeword
    from openwakeword.utils import AudioFeatures
    base = r"C:\Users\楼听\Desktop\git\JarvisAi\openWakeWord\output\aili_xiya_v0.1"
    model = openwakeword.Model(wakeword_models=[base + "\\" + "aili_xiya_v0.1.onnx"])
    # find test clips
    pos = sorted(glob.glob(base + "\\positive_test\\*.wav"))[:3]
    neg = sorted(glob.glob(base + "\\negative_test\\*.wav"))[:3]
    P(f"pos clips: {[p.split(chr(92))[-1] for p in pos]}")
    P(f"neg clips: {[p.split(chr(92))[-1] for p in neg]}")
    # 1) load path used by Model — inspect what torchaudio returns
    import torchaudio
    for w in [pos[0], neg[0]]:
        try:
            x, sr = torchaudio.load(w)
            P(f"torchaudio.load({w.split(chr(92))[-1]}): shape={tuple(x.shape)} sr={sr} absmax={float(x.abs().max()):.4f} mean={float(x.mean()):.4f}")
        except Exception as e:
            P(f"torchaudio.load({w.split(chr(92))[-1]}) RAISED: {type(e).__name__}: {e}")
    # 2) AudioFeatures embed on a raw clip (same path Model.predict_clip uses internally)
    F = AudioFeatures(device='cpu')
    for w in [pos[0], neg[0]]:
        feats = F.embed_clips([w], batch_size=1)
        a = np.asarray(feats[0]) if isinstance(feats, list) else np.asarray(feats)
        P(f"embed_clips({w.split(chr(92))[-1]}): shape={a.shape} mean={float(a.mean()):.4f} std={float(a.std()):.4f} min={float(a.min()):.3f} max={float(a.max()):.3f}")
    # 3) what Model.predict_clip returns per chunk
    preds = model.predict_clip(pos[0], padding=1, chunk_size=1280)
    P(f"predict_clip(pos): {len(preds)} chunks; first={preds[0]}; last={preds[-1]}")
    preds_n = model.predict_clip(neg[0], padding=1, chunk_size=1280)
    P(f"predict_clip(neg): {len(preds_n)} chunks; first={preds_n[0]}; last={preds_n[-1]}")
    # 4) training .npy reference stats
    p = np.load(base + "\\" + "positive_features_train.npy", mmap_mode="r")
    P(f"train pos features: shape={p.shape} mean={float(np.asarray(p).mean()):.4f} std={float(np.asarray(p).std()):.4f}")
    out.write("DONE\n")
except Exception:
    P("EXCEPTION:")
    P(traceback.format_exc())
out.close()
