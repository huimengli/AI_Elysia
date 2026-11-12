r"""v0.5 抗干扰后训练特征：把 v0.4 目录里新增的真人 clip（编号 10xx）与 SNR 混合 clip（11xx）
算成**流式滑窗特征**，与 v0.4 特征合并成 v0.5 训练/验收集。

- 特征管线：完全复用 `_t2_stream_features_v02.py`（1 s 零填充 + 1280 滑窗，chunk-boundary last-24 帧，
  与 openwakeword.Model.predict_clip 一致，HB-027）
- 真人样本权重：真人 clip（编号 10xx）行重复 ×5，SNR 混合 clip（11xx）×2；合成既有行不变
  （v0.4 的教训：真人只有 24/108 行，混在 24000/57600 行里几乎采不到，训练改动被淹没）
- 输出训练脚本要求的固定文件名（不新造结构）：
  openWakeWord/output/aili_xiya_v0.5/{positive,negative}_features_{train,test}.npy + val_fp.npy

Run:  .venv\Scripts\python.exe _t2_v05_features.py
"""
import os
import re
import shutil
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import _t2_stream_features_v02 as sf  # noqa: E402
from openwakeword.utils import AudioFeatures  # noqa: E402

V4 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.4")
V5 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.5")
SUBS = ("positive_train", "positive_test", "negative_train", "negative_test")
RE_REAL = re.compile(r"_(10\d\d)\.wav$")
RE_NOISY = re.compile(r"_(11\d\d)\.wav$")


def rows_for(sub: str, positive: bool, F):
    d = os.path.join(V4, sub)
    files = sorted(os.listdir(d)) if os.path.isdir(d) else []
    files = [f for f in files if f.endswith(".wav")]
    out = []
    for f in files:
        data = sf.load_wav(os.path.join(d, f))
        frames, bounds = sf.stream(F, data)
        M = frames.shape[0]
        spf = (sf.WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = sf.voiced_range(data, spf) if positive else None
        ws = sf.clip_windows(frames, vr, positive, bounds)
        if not ws:
            continue
        rep = 5 if RE_REAL.search(f) else (2 if RE_NOISY.search(f) else 1)
        out.extend([(np.stack(ws, axis=0), rep)])
    if not out:
        return np.zeros((0, sf.NFR, 96), np.float32), 0
    rows = []
    for arr, rep in out:
        for _ in range(rep):
            rows.append(arr)
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out)} clips -> {merged.shape[0]} rows (含真人×5/带噪×2 重复)", flush=True)
    return merged, len(out)


def main() -> int:
    os.makedirs(V5, exist_ok=True)
    F = AudioFeatures(inference_framework="onnx", ncpu=1)
    prefix = sf.measure_prefix(F)
    print(f"[init] prefix frames: {prefix}", flush=True)

    pos = {"positive_train": True, "positive_test": True,
           "negative_train": False, "negative_test": False}
    new = {s: rows_for(s, pos[s], F)[0] for s in SUBS}

    names = {"positive_train": "positive_features_train.npy",
             "positive_test": "positive_features_test.npy",
             "negative_train": "negative_features_train.npy",
             "negative_test": "negative_features_test.npy"}
    for sub, name in names.items():
        old = np.load(os.path.join(V4, name))
        if old.shape[1:] != new[sub].shape[1:]:
            print(f"FAIL: shape mismatch {sub} {old.shape} vs {new[sub].shape}")
            return 1
        merged = np.concatenate([old, new[sub]], axis=0).astype(np.float32)
        np.save(os.path.join(V5, name), merged)
        print(f"[merge] {name}: {old.shape[0]} + {new[sub].shape[0]} -> {merged.shape[0]}", flush=True)

    shutil.copy(os.path.join(V4, "val_fp.npy"), os.path.join(V5, "val_fp.npy"))
    print(f"[val_fp] copied -> {os.path.join(V5, 'val_fp.npy')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
