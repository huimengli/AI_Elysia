r"""v0.4 数据第二步：真人 clip 的**流式滑窗特征**，与 v0.3 特征合并成 v0.4 训练集。

特征管线完全复用 `_t2_stream_features_v02.py`（与 openwakeword.Model.predict_clip 一致的
1 s 零填充 + 1280 样本滑窗、chunk-boundary last-24 帧），保证训练/推理特征分布一致
（HB-027 的教训：v0.2 用整段 batch 特征训练 → 验收恒 1.0）。

输出（训练脚本要求的固定文件名，AGENTS 不发明新结构）：
  openWakeWord/output/aili_xiya_v0.4/positive_features_train.npy
  openWakeWord/output/aili_xiya_v0.4/positive_features_test.npy
  openWakeWord/output/aili_xiya_v0.4/negative_features_train.npy
  openWakeWord/output/aili_xiya_v0.4/negative_features_test.npy
  openWakeWord/output/aili_xiya_v0.4/val_fp.npy（复制 v0.3 的 5 分钟背景混音）

Run:  .venv\Scripts\python.exe _t2_v04_features.py
"""
import os
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
V4 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.4")


def rows_for(sub: str, positive: bool, F) -> np.ndarray:
    d = os.path.join(V4, sub)
    files = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".wav"))
    rows = []
    for p in files:
        data = sf.load_wav(p)
        frames, bounds = sf.stream(F, data)
        M = frames.shape[0]
        spf = (sf.WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = sf.voiced_range(data, spf) if positive else None
        rows.extend(sf.clip_windows(frames, vr, positive, bounds))
    if not rows:
        return np.zeros((0, sf.NFR, 96), np.float32)
    arr = np.stack(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(files)} clips -> {arr.shape[0]} rows shape={arr.shape}", flush=True)
    return arr


def main() -> int:
    F = AudioFeatures(inference_framework="onnx", ncpu=1)
    prefix = sf.measure_prefix(F)
    print(f"[init] prefix frames (random init + 1 s warmup): {prefix}", flush=True)

    new = {}
    for sub, pos in (("positive_train", True), ("positive_test", True),
                     ("negative_train", False), ("negative_test", False)):
        new[sub] = rows_for(sub, pos, F)

    old = {}
    for sub, name in (("positive_train", "positive_features_train.npy"),
                      ("positive_test", "positive_features_test.npy"),
                      ("negative_train", "negative_features_train.npy"),
                      ("negative_test", "negative_features_test.npy")):
        p = os.path.join(V3, name)
        a = np.load(p)
        old[sub] = a
        print(f"[v0.3] {name} rows={a.shape[0]} shape={a.shape}", flush=True)

    for sub, name in (("positive_train", "positive_features_train.npy"),
                      ("positive_test", "positive_features_test.npy"),
                      ("negative_train", "negative_features_train.npy"),
                      ("negative_test", "negative_features_test.npy")):
        if old[sub].shape[1:] != new[sub].shape[1:]:
            print(f"FAIL: shape mismatch {sub} {old[sub].shape} vs {new[sub].shape}")
            return 1
        merged = np.concatenate([old[sub], new[sub]], axis=0).astype(np.float32)
        out = os.path.join(V4, name)
        np.save(out, merged)
        print(f"[merge] {name}: {old[sub].shape[0]} + {new[sub].shape[0]} -> {merged.shape[0]} -> {out}", flush=True)

    shutil.copy(os.path.join(V3, "val_fp.npy"), os.path.join(V4, "val_fp.npy"))
    print(f"[val_fp] copied v0.3 val_fp.npy -> {os.path.join(V4, 'val_fp.npy')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
