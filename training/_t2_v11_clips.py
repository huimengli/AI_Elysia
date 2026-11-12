r"""v1.1 数据第一步：多音色 TTS 件（2026-11-12 18:49/19:23 需求）按判据切 15xx clip。

来源：`.tmp/v11tts/<音色>__<kind>__<slug>.wav`（16k mono，`training/_t2_v11_tts.py` 生成）。

**判据（本批口径，与 Q14 推荐一致，先测后训）**：

- **正样本（kind=pos）**：v0.9 部署管线检出 >=1 且 **3 实例峰值中位数 >=0.70** → 该音色模型有响应，入库可扩宽召回
- **负样本（neg_near/neg_comp/neg_unrel）**：**3 实例峰值全 <0.70** → 可安全入库；任一次 >=0.70（与真唤醒 0.82 量级）→ **不入库**（v1.0 recall 0.3009 塌陷机制）
- 件长即 clip（1.3-3.7 s，GSV/Kokoro 单句），不再切窗；train/test 按音色交替对半分
- 编号 15xx（沿用既有前缀，不新造约定，AGENTS §0）：`posx_tr_` / `pos_te_` / `negx_tr_` / `negx_te_`

Run:  .venv\Scripts\python.exe training\_t2_v11_clips.py
"""
import os
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
SR = 16000
CHUNK = 1280
THR = 0.70
GAP = 2.0
NINST = 3
SRC = os.path.join(ROOT, ".tmp", "v11tts")
V11 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.1")
SCORER = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9", "aili_xiya_v0.9.onnx")

POS_ID = [1500]
NEG_ID = [1500]


def load_wav(p):
    with wave.open(p, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def save(data, sub, name):
    d = os.path.join(V11, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())
    return p


def rms(a):
    return float(np.sqrt(np.mean(a.astype(np.float32) ** 2)))


def main() -> int:
    import openwakeword
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".wav") and "__" in f)
    if not files:
        print("FAIL: 无生成件", flush=True)
        return 1

    # **逐件新建实例打分**（HB-032 播种独立性）；连续流式复用实例会把上一件 mel 缓冲带进
    # 下一件、检出后 reset 清零缓冲，实测把正样本峰值从 0.873 压到 0.483 —— 不可比（2026-11-12 20:35）。
    # 一次性 560 次构造会 onnxruntime `bad allocation`，故用完即 `del` + `gc.collect()`。
    import gc
    results = []
    for f in files:
        audio = load_wav(os.path.join(SRC, f))
        m = openwakeword.Model(wakeword_models=[SCORER], inference_framework="onnx", ncpu=1)
        nd, last = 0, -10**9
        for i in range(0, max(1, len(audio) - CHUNK), CHUNK):
            s0 = float(m.predict(audio[i:i + CHUNK]).get("aili_xiya_v0.9", 0.0))
            if s0 >= THR and i - last >= GAP * SR:
                nd += 1
                last = i
                m.reset()
        del m
        pk = []
        for _ in range(NINST):
            m = openwakeword.Model(wakeword_models=[SCORER], inference_framework="onnx", ncpu=1)
            pk.append(max(float(m.predict(audio[i:i + CHUNK]).get("aili_xiya_v0.9", 0.0))
                          for i in range(0, max(1, len(audio) - CHUNK), CHUNK)))
            del m
        results.append((f, nd, sorted(pk)))
        gc.collect()

    kept = 0
    drop = 0
    n_pos = 0
    n_neg = 0
    for f, nd, pk in results:
        audio = load_wav(os.path.join(SRC, f))
        timbre, kind, slug = f[:-4].split("__")
        pos = kind == "pos"
        ok = (nd >= 1 and pk[1] >= THR) if pos else (pk[2] < THR)
        if not ok:
            drop += 1
            print(f"  不入库 {timbre:9s} {kind:9s} {slug:16s} dur={len(audio)/SR:.2f}s 检出={nd} "
                  f"3实例峰值={pk[0]:.3f}/{pk[1]:.3f}/{pk[2]:.3f}", flush=True)
            continue
        # train/test 按类别交替对半分（同类内部，不依赖音色）
        split = "train" if ((n_pos if pos else n_neg) % 2 == 0) else "test"
        if pos:
            n_pos += 1
            name = (f"posx_tr_{POS_ID[0]}" if split == "train" else f"pos_te_{POS_ID[0]}")
            POS_ID[0] += 1
            sub = "positive_train" if split == "train" else "positive_test"
        else:
            n_neg += 1
            name = (f"negx_tr_{NEG_ID[0]}" if split == "train" else f"negx_te_{NEG_ID[0]}")
            NEG_ID[0] += 1
            sub = "negative_train" if split == "train" else "negative_test"
        save(audio, sub, name + ".wav")
        kept += 1
        print(f"  入库({split}) {timbre:9s} {kind:9s} {slug:16s} dur={len(audio)/SR:.2f}s "
              f"rms={rms(audio):.0f} 检出={nd} 峰值={pk[0]:.3f}/{pk[1]:.3f}/{pk[2]:.3f} -> {name}.wav", flush=True)

    print(f"\n入库 {kept} 件 / 不入库 {drop} 件 -> {V11}", flush=True)
    print(f"posx 用号 {POS_ID[0]} / negx 用号 {NEG_ID[0]}", flush=True)
    for sub in ("positive_train", "positive_test", "negative_train", "negative_test"):
        d = os.path.join(V11, sub)
        n = len([x for x in os.listdir(d) if x.endswith(".wav")]) if os.path.isdir(d) else 0
        print(f"[wavs] {sub}: {n}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
