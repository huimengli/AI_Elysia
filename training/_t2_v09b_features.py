r"""v0.9b 特征：把 1 小时录音法的 12 段真实负样本并入 **v0.9** 特征集（2026-11-19 14:26 需求）。

依据 records/2026-11-19-13-10-55.md 的 14:26 追加节：你逐字「听过了,全都是真实的负样本」→ **授权破**
「负样本 3 实例峰值全 <0.70 才入库；任一次 >=0.70 不入库」（train_config_v12.yaml + v1.0 Recall 0.3009 教训），
把这 12 段（10 段实测越线 + 2 段三实例不越线）**全部作为负样本入库**。

**照现成管线，不造新约定（AGENTS §0）**：

- 基线 = `aili_xiya_v0.9` 的 4 个 npy（照 `training/_t2_v11_features.py:71-84` 的 merge 做法）；
- 新负样本命名照现成约定 `negx_tr_16xx.wav` / `negx_te_16xx.wav`（现有 negx id 最大 1549 → 用 16xx 块）；
- train/test 切分：**按时间顺序交替**（第 1、3、5… 段进 train，第 2、4、6… 段进 test），各 6 件，
  写死在代码里，落盘在 record；
- **负样本权重 1（`RENEG = 1`，HB-021）**；逐件流式（HB-027，`_t2_stream_features_v02` 的 `stream` + `clip_windows`，
  neg 保留全部候选窗口、按 MAXW=12 均匀上限）；
- 正样本本轮**没有新增**（v0.9 正样本原样继承），所以 positive npy 直接继承 v0.9，不产生新增行。

Run:  .venv\Scripts\python.exe training\_t2_v09b_features.py
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
V9B = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9b")
SRC = os.path.join(ROOT, ".tmp", "hb51_audio")
RENEG = 1

NAMES = {"positive_train": "positive_features_train.npy",
         "positive_test": "positive_features_test.npy",
         "negative_train": "negative_features_train.npy",
         "negative_test": "negative_features_test.npy"}

# 时间顺序（昨天手机视频 3 段在前，今天 1 小时 9 段在后）
SEGMENTS = ["seg_203413_1.wav", "seg_203623_14.wav", "seg_203633_15.wav", "seg_102830_1.wav",
            "seg_120007_29.wav", "seg_120117_36.wav", "seg_120127_37.wav", "seg_120157_40.wav",
            "seg_120917_84.wav", "seg_121337_110.wav", "seg_121417_114.wav", "seg_122027_151.wav"]


def split() -> dict:
    """第 1,3,5.. 段 -> negative_train（negx_tr_1600,1602..）；第 2,4,6.. -> negative_test
    （negx_te_1601,1603..）。写死、可复算。"""
    out = {"negative_train": [], "negative_test": []}
    for i, seg in enumerate(SEGMENTS):
        n = 1600 + 2 * (i // 2) + (0 if i % 2 == 0 else 1)
        sub = "negative_train" if i % 2 == 0 else "negative_test"
        out[sub].append((seg, f"negx_{'tr' if i % 2 == 0 else 'te'}_{n}.wav"))
    return out


def rows_for(sub, files):
    d = os.path.join(V9B, sub)
    out = []
    for f in files:
        data = sf.load_wav(f)
        frames, bounds = sf.stream(F, data)
        M = frames.shape[0]
        spf = (sf.WARMUP * 2 + data.shape[0]) / max(M, 1)
        ws = sf.clip_windows(frames, None, False, bounds)
        if not ws:
            print(f"  [{sub}] {os.path.basename(f)} 无窗口（过短）", flush=True)
            continue
        out.append((np.stack(ws, axis=0), RENEG))
        print(f"  [{sub}] {os.path.basename(f)} {len(ws)} 窗口（10 s 件，MAXW={sf.MAXW} 上限）", flush=True)
    if not out:
        return np.zeros((0, sf.NFR, 96), np.float32)
    rows = [arr for arr, rep in out for _ in range(rep)]
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out)} clips -> {merged.shape[0]} rows (rep={RENEG})", flush=True)
    return merged


def main() -> int:
    os.makedirs(V9B, exist_ok=True)
    for sub in ("positive_train", "positive_test", "negative_train", "negative_test"):
        os.makedirs(os.path.join(V9B, sub), exist_ok=True)

    sp = split()
    for sub, pairs in sp.items():
        d = os.path.join(V9B, sub)
        for seg, newname in pairs:
            src = os.path.join(SRC, seg)
            if not os.path.exists(src):
                print(f"FAIL: 源段不存在 {src}", flush=True)
                return 1
            shutil.copy(src, os.path.join(d, newname))
            print(f"[copy] {seg} -> {sub}/{newname}", flush=True)

    global F
    F = AudioFeatures(inference_framework="onnx", ncpu=1)
    print(f"[init] prefix frames: {sf.measure_prefix(F)}", flush=True)

    new = {s: rows_for(s, [os.path.join(V9B, s, n) for _, n in sp[s]])
           for s in ("negative_train", "negative_test")}

    for sub, name in NAMES.items():
        old = np.load(os.path.join(V9, name))
        if sub in new:
            if new[sub].shape[0] == 0:
                print(f"FAIL: {sub} 新增 0 行", flush=True)
                return 1
            if old.shape[1:] != new[sub].shape[1:]:
                print(f"FAIL: shape mismatch {sub} {old.shape} vs {new[sub].shape}", flush=True)
                return 1
            merged = np.concatenate([old, new[sub]], axis=0).astype(np.float32)
            print(f"[merge] {name}: v0.9 {old.shape[0]} + new {new[sub].shape[0]} -> {merged.shape[0]}", flush=True)
        else:
            merged = old  # 正样本本轮无新增，原样继承 v0.9
            print(f"[inherit] {name}: v0.9 {old.shape[0]} 行（本轮无新增正样本）", flush=True)
        np.save(os.path.join(V9B, name), merged)

    shutil.copy(os.path.join(V9, "val_fp.npy"), os.path.join(V9B, "val_fp.npy"))
    print("[val_fp] copied from v0.9", flush=True)
    for sub in ("negative_train", "negative_test"):
        n = len([f for f in os.listdir(os.path.join(V9B, sub)) if f.endswith(".wav")])
        print(f"[wavs] {sub}: {n} 件（v0.9 原有 + 本次 12 段分到的件）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
