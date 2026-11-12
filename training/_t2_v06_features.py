r"""v0.6 特征：13 条真人呼唤（12xx 中 120x）+ 52 条带噪呼唤（121x）算成流式滑窗特征，
与 **v0.3 的合成特征**（不是 v0.4/v0.5——那两批把真呼唤当负样本，必须丢弃）合并成 v0.6 集。

- 特征管线完全复用 `_t2_stream_features_v02.py`（1 s 零填充 + 1280 滑窗、chunk-boundary last-24 帧，
  与 openwakeword.Model.predict_clip 一致，HB-027；`AudioFeatures(onnx, ncpu=1)`，prefix 53 / NFR 24）
- 行重复：真人原样本（`*_120x`）×5，带噪样本（`*_121x`）×2（v0.4 教训：真人行数太少会被 24000 行合成淹没）
- 负样本：v0.3 合成对抗样本（既有 npy）+ 本录音定标出的纯噪声窗口（`noise_tr_1210-1213` / `noise_te_1210-1213`）
- 输出训练脚本要求的固定文件名（不新造结构）：
  openWakeWord/output/aili_xiya_v0.6/{positive,negative}_features_{train,test}.npy + val_fp.npy

Run:  .venv\Scripts\python.exe _t2_v06_features.py
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

V3 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.3")
V6 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.6")
SUBS = ("positive_train", "positive_test", "negative_train", "negative_test")
RE_REAL = re.compile(r"_120\d\.wav$")
RE_NOISY = re.compile(r"_121\d\.wav$")


def rows_for(sub: str, positive: bool, F):
    d = os.path.join(V6, sub)
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
        out.append((np.stack(ws, axis=0), rep))
    if not out:
        return np.zeros((0, sf.NFR, 96), np.float32), 0
    rows = []
    for arr, rep in out:
        for _ in range(rep):
            rows.append(arr)
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out)} clips -> {merged.shape[0]} rows (真人×5/带噪×2)", flush=True)
    return merged, len(out)


def main() -> int:
    os.makedirs(V6, exist_ok=True)
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
        old = np.load(os.path.join(V3, name))
        if old.shape[1:] != new[sub].shape[1:]:
            print(f"FAIL: shape mismatch {sub} {old.shape} vs {new[sub].shape}", flush=True)
            return 1
        merged = np.concatenate([old, new[sub]], axis=0).astype(np.float32)
        np.save(os.path.join(V6, name), merged)
        print(f"[merge] {name}: v0.3 {old.shape[0]} + v0.6 {new[sub].shape[0]} -> {merged.shape[0]}",
              flush=True)

    shutil.copy(os.path.join(V3, "val_fp.npy"), os.path.join(V6, "val_fp.npy"))
    print(f"[val_fp] copied -> {os.path.join(V6, 'val_fp.npy')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
