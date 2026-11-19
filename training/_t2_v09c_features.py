r"""v0.9c 特征：把 2026-11-19 第 2 轮录音里「三实例都出现越线」的 9 段并入 **v0.9** 特征集（18:24 你的选择）。

依据 records/2026-11-19-15-18-21.md 的 18:24 追加节：你逐字选项「只入三实例交集的 9 段（推荐）」→
9 件作硬负样本；5 段「无三实例交集」的边界带**不入**，丢弃段里 8 段 peak >=0.70 **不入**（照 2026-11-17 判据
「负样本 3 实例峰值全 <0.70 才入库；任一次 >=0.70 -> 不入库」）。

**基线 = v0.9 特征集 + 这 9 件**；v0.9b 的 12 段**不带入**（照「特征带入=禁止」口径，等你纠正）。

**照现成管线，不造新约定（AGENTS §0）**：

- merge 做法照 `training/_t2_v11_features.py:71-84` 与 `training/_t2_v09b_features.py`；
- 命名照现成约定 `negx_tr_16xx.wav` / `negx_te_16xx.wav`（现有 negx id 最大 1610/1611 → 接续 1612 起）；
- train/test 切分：**按时间顺序交替**（第 1、3、5、7、9 段进 train，第 2、4、6、8 段进 test），5 train / 4 test，
  写死在代码里，落盘在 record；
- **负样本权重 1（`RENEG = 1`，HB-021）**；逐件流式（HB-027，`_t2_stream_features_v02` 的 `stream` + `clip_windows`，
  neg 保留全部候选窗口、按 MAXW=12 均匀上限）；
- 正样本本轮**没有新增**（v0.9 正样本原样继承），并且照现成做法把 v0.9 的正样本 wav（4 train / 1 test）
  复制进 v0.9c 目录 —— 训练脚本第 944-947 行**无条件**读 `positive_test` 的 wav 算件长，目录空会
  `ValueError: high <= 0`（2026-11-19 14:xx 实测自曝第 2 处）。

Run:  .venv\Scripts\python.exe training\_t2_v09c_features.py
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
V9C = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9c")
SRC = os.path.join(ROOT, ".tmp", "hb51_audio")
RENEG = 1

NAMES = {"positive_train": "positive_features_train.npy",
         "positive_test": "positive_features_test.npy",
         "negative_train": "negative_features_train.npy",
         "negative_test": "negative_features_test.npy"}

# 时间顺序；只列三实例都出现越线的 9 段（16:22 位置表，stable_positions_1622.py 解析）
SEGMENTS = ["seg_153229_62.wav", "seg_153349_70.wav", "seg_153509_78.wav", "seg_153539_81.wav",
            "seg_153839_99.wav", "seg_153849_100.wav", "seg_154249_124.wav", "seg_155109_174.wav",
            "seg_160229_242.wav"]

# 三实例稳定越线时刻（秒/峰值），逐字照 16:22 位置表，落盘可复核
STABLE = {"seg_153229_62.wav": "4.72/0.779", "seg_153349_70.wav": "5.84/0.785",
          "seg_153509_78.wav": "4.96/0.771", "seg_153539_81.wav": "8.96/0.787",
          "seg_153839_99.wav": "4.16/0.795", "seg_153849_100.wav": "6.56/0.789",
          "seg_154249_124.wav": "8.8/0.76", "seg_155109_174.wav": "8.72/0.773",
          "seg_160229_242.wav": "3.92/0.77"}

POS_WAVS = {"positive_train": ["posx_tr_1300.wav", "posx_tr_1301.wav", "posx_tr_1302.wav",
                               "posx_tr_1303.wav"],
            "positive_test": ["pos_te_1300.wav"]}


def split() -> dict:
    """第 1,3,5,7,9 段 -> negative_train（negx_tr_1612,1614,1616,1618,1620）；
    第 2,4,6,8 段 -> negative_test（negx_te_1613,1615,1617,1619）。写死、可复算。"""
    out = {"negative_train": [], "negative_test": []}
    for i, seg in enumerate(SEGMENTS):
        n = 1612 + 2 * (i // 2) + (0 if i % 2 == 0 else 1)
        sub = "negative_train" if i % 2 == 0 else "negative_test"
        tag = "tr" if i % 2 == 0 else "te"
        out[sub].append((seg, f"negx_{tag}_{n}.wav"))
    return out


def rows_for(sub, files):
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
        print(f"  [{sub}] {os.path.basename(f)} {len(ws)} 窗口（10 s 件，MAXW={sf.MAXW} 上限）"
              f" 稳定越线 {STABLE.get(os.path.basename(f), '?')}", flush=True)
    if not out:
        return np.zeros((0, sf.NFR, 96), np.float32)
    rows = [arr for arr, rep in out for _ in range(rep)]
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out)} clips -> {merged.shape[0]} rows (rep={RENEG})", flush=True)
    return merged


def main() -> int:
    os.makedirs(V9C, exist_ok=True)
    for sub in ("positive_train", "positive_test", "negative_train", "negative_test"):
        os.makedirs(os.path.join(V9C, sub), exist_ok=True)

    # 照现成做法把 v0.9 正样本 wav 原样复制（训练脚本第 944-947 行需要 positive_test 里有 wav）
    for sub, names in POS_WAVS.items():
        for nm in names:
            src = os.path.join(V9, sub, nm)
            if not os.path.exists(src):
                print(f"FAIL: v0.9 正样本 wav 不存在 {src}", flush=True)
                return 1
            shutil.copy(src, os.path.join(V9C, sub, nm))
            print(f"[copy-pos] {sub}/{nm}", flush=True)

    sp = split()
    for sub, pairs in sp.items():
        d = os.path.join(V9C, sub)
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

    new = {s: rows_for(s, [os.path.join(V9C, s, n) for _, n in sp[s]])
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
            print(f"[merge] {name}: v0.9 {old.shape[0]} + new {new[sub].shape[0]} -> {merged.shape[0]}",
                  flush=True)
        else:
            merged = old  # 正样本本轮无新增，原样继承 v0.9
            print(f"[inherit] {name}: v0.9 {old.shape[0]} 行（本轮无新增正样本）", flush=True)
        np.save(os.path.join(V9C, name), merged)

    shutil.copy(os.path.join(V9, "val_fp.npy"), os.path.join(V9C, "val_fp.npy"))
    print("[val_fp] copied from v0.9", flush=True)
    for sub in ("negative_train", "negative_test"):
        n = len([f for f in os.listdir(os.path.join(V9C, sub)) if f.endswith(".wav")])
        print(f"[wavs] {sub}: {n} 件（v0.9 原有 + 本次 9 段分到的件）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
