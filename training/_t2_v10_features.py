r"""v1.0 特征：2026-11-12 17:10-17:22 真人补录（19 正 / 5 正留出 / 4 真人负 / 6 噪声窗）并入 v0.9 集。

依据 records/2026-11-12-17-22-40.md 的判据与 `ai_buckup/onnx_opinion.md` 第 5 节结论：

- **行重复比只移动灵敏度曲线，不产生近音判别力**（v0.7 负 ×5 → 检出 10→5；v0.8 正 ×5/负 ×3 → 近音 fp 3/3；
  v0.9 正 ×5/负 ×2 → 检出 14 但近音 fp 9-11）。所以本批**正样本 ×5、新真人负样本 ×1**，不再加大负样本
  重复比，先看新数据的真实判别力，避免把灵敏度曲线整体推走。
- **真人件不按峰值剔除**（`negx_tr_1402` 米雅峰值 0.827，与真呼唤整段峰值同量级，仍按文件名真值入库）。
- **TTS 合成件不入库**（长期结论）。本批全部是真人录音，无合成件。
- 管线与 `_t2_stream_features_v02.py` 一致（HB-027：逐件流式算特征，不用批式），
  HB-028：训练脚本要求 positive_* 目录里有 wav（本批 clip 已在目录中）。

Run:  .venv\Scripts\python.exe training\_t2_v10_features.py
"""
import os
import shutil
import sys

import numpy as np

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import _t2_stream_features_v02 as sf  # noqa: E402
from openwakeword.utils import AudioFeatures  # noqa: E402

V9 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9")
V10 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.0")
SUBS = ("positive_train", "positive_test", "negative_train", "negative_test")
REPOS = 5
RENEG = 1

NAMES = {"positive_train": "positive_features_train.npy",
         "positive_test": "positive_features_test.npy",
         "negative_train": "negative_features_train.npy",
         "negative_test": "negative_features_test.npy"}


def rows_for(sub, positive, F):
    d = os.path.join(V10, sub)
    files = [os.path.join(d, f) for f in sorted(os.listdir(d))
            if f.endswith(".wav") and (f.startswith("pos") if positive else True)]
    out = []
    for f in files:
        data = sf.load_wav(f)
        frames, bounds = sf.stream(F, data)
        M = frames.shape[0]
        spf = (sf.WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = sf.voiced_range(data, spf) if positive else None
        ws = sf.clip_windows(frames, vr, positive, bounds)
        if not ws:
            print(f"  [{sub}] {os.path.basename(f)} 无窗口（过短）", flush=True)
            continue
        out.append((np.stack(ws, axis=0), REPOS if positive else RENEG))
    if not out:
        return np.zeros((0, sf.NFR, 96), np.float32)
    rows = [arr for arr, rep in out for _ in range(rep)]
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out)} clips -> {merged.shape[0]} rows (rep={REPOS if positive else RENEG})", flush=True)
    return merged


def main() -> int:
    os.makedirs(V10, exist_ok=True)
    F = AudioFeatures(inference_framework="onnx", ncpu=1)
    print(f"[init] prefix frames: {sf.measure_prefix(F)}", flush=True)

    pos = {"positive_train": True, "positive_test": True,
           "negative_train": False, "negative_test": False}
    new = {s: rows_for(s, pos[s], F) for s in SUBS}

    for sub, name in NAMES.items():
        old = np.load(os.path.join(V9, name))
        if new[sub].shape[0] == 0:
            print(f"FAIL: {sub} 新增 0 行", flush=True)
            return 1
        if old.shape[1:] != new[sub].shape[1:]:
            print(f"FAIL: shape mismatch {sub} {old.shape} vs {new[sub].shape}", flush=True)
            return 1
        merged = np.concatenate([old, new[sub]], axis=0).astype(np.float32)
        np.save(os.path.join(V10, name), merged)
        print(f"[merge] {name}: v0.9 {old.shape[0]} + new {new[sub].shape[0]} -> {merged.shape[0]}", flush=True)

    shutil.copy(os.path.join(V9, "val_fp.npy"), os.path.join(V10, "val_fp.npy"))
    print("[val_fp] copied from v0.9", flush=True)
    for sub in ("positive_train", "positive_test", "negative_train", "negative_test"):
        n = len([f for f in os.listdir(os.path.join(V10, sub)) if f.endswith(".wav")])
        print(f"[wavs] {sub}: {n} 件真人 clip", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
