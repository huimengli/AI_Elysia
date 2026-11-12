r"""v1.0b 特征：17:22 批的 14xx clip 并入 **v0.9** 基线，并按 Q14 裁决（选项 1）剔除高分真人件。

Q14 定案（need_user.md，2026-11-12 21:40，用户原话「尝试 1」）：
「真人件按文件名真值入库，**峰值 >= 0.80（真呼唤整段峰值量级）的件只作验收集、不入训练集**。」

14xx 清单与判定（v0.9 @3 独立实例峰值，取自 `.tmp/bats/v10_clips.log`）：

| clip | 来源 | 峰值 | 处理 |
| --- | --- | --- | --- |
| posx_tr_1400-1418 / pos_te_1400-1405 | 14 次件、键盘 4 次件、6 件带噪呼唤 | 0.619-0.877 | **入库 ×5** |
| negx_tr_1400 | 真人近音 `爱你老师` | 0.756 | 入库 ×1 |
| **negx_tr_1401** | 真人近音 `雅诗兰黛` | **0.822** | **剔除，只作验收集** |
| **negx_tr_1402** | 真人近音 `米雅` | **0.827** | **剔除，只作验收集** |
| negx_tr_1403 | 竞品唤醒 `天猫精灵` | 0.678 | 入库 ×1 |
| negx_te_1400 | 应答语 `我没听清` | 0.719 | 入库 ×1 |
| noise_tr_1404-1406 | 机械键盘噪音低分窗 | 0.709 / 0.689 / 0.692 | 入库 ×1 |
| noise_tr_1407-1409 | 环境音低分窗 | 0.623 / 0.664 / 0.697 | 入库 ×1 |

管线与 `_t2_stream_features_v02.py` / `_t2_v11_features.py` 完全一致（HB-027 逐件流式，HB-028 目录内要放 wav）。

Run:  .venv\Scripts\python.exe training\_t2_v10b_features.py
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
V10B = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.0b")
SUBS = ("positive_train", "positive_test", "negative_train", "negative_test")
REPOS = 5
RENEG = 1

# Q14 选项 1：峰值 >= 0.80 的真人件只作验收集
EXCLUDE = {
    "negx_tr_1401.wav": "雅诗兰黛 峰值 0.822（>=0.80，与真唤醒同量级）→ 验收集",
    "negx_tr_1402.wav": "米雅 峰值 0.827（>=0.80，与真唤醒同量级）→ 验收集",
}

NAMES = {"positive_train": "positive_features_train.npy",
         "positive_test": "positive_features_test.npy",
         "negative_train": "negative_features_train.npy",
         "negative_test": "negative_features_test.npy"}


def rows_for(sub, positive, F):
    d = os.path.join(V10, sub)
    files = sorted(f for f in os.listdir(d) if f.endswith(".wav"))
    keep = []
    for f in files:
        if f in EXCLUDE:
            print(f"  [{sub}] 剔除 {f}：{EXCLUDE[f]}", flush=True)
            continue
        keep.append(f)
    out = []
    for f in keep:
        data = sf.load_wav(os.path.join(d, f))
        frames, bounds = sf.stream(F, data)
        M = frames.shape[0]
        spf = (sf.WARMUP * 2 + data.shape[0]) / max(M, 1)
        vr = sf.voiced_range(data, spf) if positive else None
        ws = sf.clip_windows(frames, vr, positive, bounds)
        if not ws:
            print(f"  [{sub}] {f} 无窗口（过短）", flush=True)
            continue
        out.append((np.stack(ws, axis=0), REPOS if positive else RENEG))
    if not out:
        return np.zeros((0, sf.NFR, 96), np.float32)
    rows = [arr for arr, rep in out for _ in range(rep)]
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out)} clips -> {merged.shape[0]} rows (rep={REPOS if positive else RENEG})", flush=True)
    return merged


def main() -> int:
    os.makedirs(V10B, exist_ok=True)
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
        np.save(os.path.join(V10B, name), merged)
        print(f"[merge] {name}: v0.9 {old.shape[0]} + new {new[sub].shape[0]} -> {merged.shape[0]}", flush=True)

    shutil.copy(os.path.join(V9, "val_fp.npy"), os.path.join(V10B, "val_fp.npy"))
    print("[val_fp] copied from v0.9", flush=True)
    for sub in SUBS:
        src = sorted(f for f in os.listdir(os.path.join(V10, sub))
                     if f.endswith(".wav") and f not in EXCLUDE)
        dst = os.path.join(V10B, sub)
        os.makedirs(dst, exist_ok=True)
        for f in src:
            shutil.copy(os.path.join(V10, sub, f), os.path.join(dst, f))
        print(f"[wavs] {sub}: {len(src)} 件 14xx clip（已剔除 {len(EXCLUDE)} 件规则外）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
