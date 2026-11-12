r"""多音色 TTS 生成件的打分与入库判定（2026-11-12 18:49/19:23 需求）。

输入：`.tmp/v11tts/<音色>__<kind>__<slug>.wav`（16k mono int16，由 `training/_t2_v11_tts.py` 生成）。
判据（本批口径，与 Q14 推荐一致）：

- **正样本（kind=pos）**：v0.9 部署管线检出 >=1 次 **且 3 实例峰值 >=0.70** -> 该音色模型有响应，**入库可扩宽召回**
- **负样本（neg_near/neg_comp/neg_unrel）**：**3 实例一致 <0.70** -> **可安全入库**；峰值 >=0.70（与真唤醒 0.82 量级）-> **不入库**（v1.0 recall 0.3009 塌陷机制）

单探针串行（并发 4 会 `_streaming_melspectrogram` MemoryError，hard_bug.md HB-032）。

Run:
  .venv\Scripts\python.exe training\_t2_v11_score.py            # 默认 aili_xiya_v0.9
  .venv\Scripts\python.exe training\_t2_v11_score.py aili_xiya_v1.0
  .venv\Scripts\python.exe training\_t2_v11_score.py --thr 0.75
"""
import os
import sys
import wave

import numpy as np

sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
import _t2_stream_features_v02 as sf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
OUT = os.path.join(ROOT, ".tmp", "v11tts")
W = os.path.join(ROOT, "openWakeWord", "output")
GAP = 2.0
NINST = 3


def load_wav(p):
    with wave.open(p, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def make_insts(name, onnx, n):
    from openwakeword.model import Model
    return [Model(wakeword_models=[onnx], inference_framework="onnx", ncpu=1) for _ in range(n)]


def scan(name, audios, onnx, thr):
    """**每件用新建实例打分**（HB-032：`AudioFeatures.__init__` 用 `np.random` 播种，随机播种=实例独立性；
    连续流式复用实例会把上一件的 mel 缓冲带进下一件、且 `reset()` 把缓冲清零，实测把 `elya__pos__ai_li_xi_ya`
    的峰值从 0.873 压到 0.483 —— 不可比，2026-11-12 20:35 实测）。

    内存做法：**逐件新建、用完即 `del` + `gc.collect()`**（连续流式复用曾 `bad allocation`，一次性 560 次构造也爆）。
    """
    import gc
    from openwakeword.model import Model
    out = []
    for f in audios:
        a = audios[f]
        m = Model(wakeword_models=[onnx], inference_framework="onnx", ncpu=1)
        ev, last = 0, -10**9
        sc = []
        for i in range(0, len(a) - 1280, 1280):
            s = float(m.predict(a[i:i + 1280])[name])
            sc.append(s)
            if s >= thr and i - last >= GAP * 16000:
                ev += 1
                last = i
                m.reset()
        del m
        pk = []
        for _ in range(NINST):
            m = Model(wakeword_models=[onnx], inference_framework="onnx", ncpu=1)
            pk.append(max(float(m.predict(a[i:i + 1280])[name]) for i in range(0, len(a) - 1280, 1280)))
            del m
        out.append((f, ev, sorted(pk)))
        gc.collect()
    return out


def main() -> int:
    thr = 0.70
    args = [a for a in sys.argv[1:]]
    models = []
    for a in args:
        if a == "--thr":
            continue
        if a.startswith("0.7") or a.startswith("0.8"):
            thr = float(a)
        elif a.startswith("aili_xiya"):
            models.append(a)
    if "--thr" in args:
        i = args.index("--thr")
        thr = float(args[i + 1])
    models = models or ["aili_xiya_v0.9"]

    files = sorted(f for f in os.listdir(OUT) if f.endswith(".wav") and f != "ref_user.wav")
    audios = {f: load_wav(os.path.join(OUT, f)) for f in files}

    for name in models:
        onnx = os.path.join(W, name, f"{name}.onnx")
        print(f"\n[{name}] 多音色件判定 @阈值 {thr}（部署管线 1280 chunk + 冷却 {GAP}s；3 实例峰值，逐件新建实例）", flush=True)
        rows = scan(name, audios, onnx, thr)
        keep, drop = [], []
        for f, ev, pk in rows:
            timbre, kind, slug = f[:-4].split("__")
            pos = kind == "pos"
            ok = (ev >= 1 and pk[1] >= thr) if pos else (pk[2] < thr)
            tag = "入库" if ok else "不入库"
            (keep if ok else drop).append(f)
            print(f"  {timbre:9s} {kind:9s} {slug:16s} dur={len(audios[f])/16000:.2f}s "
                  f"rms={np.sqrt(np.mean(audios[f].astype(np.float32)**2)):.0f} 检出={ev} "
                  f"3实例峰值={pk[0]:.3f}/{pk[1]:.3f}/{pk[2]:.3f} -> {tag}", flush=True)
        print(f"\n  汇总 [{name}] @{thr}：可入库 {len(keep)} 件 / 生成 {len(files)} 件", flush=True)
        for timbre in sorted({f.split('__')[0] for f in files}):
            kp = [f for f in keep if f.startswith(timbre + "__pos__")]
            kn = [f for f in keep if f.startswith(timbre + "__neg")]
            tp = [f for f in files if f.startswith(timbre + "__pos__")]
            tn = [f for f in files if f.startswith(timbre + "__neg")]
            print(f"    {timbre}: 正样本 {len(kp)}/{len(tp)} 入库，负样本 {len(kn)}/{len(tn)} 入库", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
