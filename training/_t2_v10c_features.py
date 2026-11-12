r"""v1.0c 特征：按 Q15 裁决（2026-11-12 22:11「改窗口约定」）重算 14xx / 15xx 合格件并入 v0.9 基线。

Q15 三条（用户批准，need_user.md Q15 status: done，归档 `ai_buckup/need_user.md_2026-11-12-22-11-29.md`）：

1. **正样本窗锚定有声段、尾音压到最短**：`[检出-0.5, 检出+1.0]`（1.5 s，含约 1 s 尾音静音）→ **截到前 0.8 s**；
2. **负样本剔除「以纯静音为主的窗」**：候选窗（24 帧 ≈ 2.7 个 1280-sample chunk）对应原始片段 RMS **< 120 的不入库**；
3. **真人近音件只作音节窗验收集**，不入训练集：`米雅`、`雅诗兰黛`、`爱你老师`（以及基线 `爱莉雅`/`米雅希`/`希雅老师`）；
   保留 `天猫精灵`（竞品唤醒）、`我没听清`（应答语）、键盘噪音与环境音低分窗。

依据（`tests/2026-11-12-21-40-35_cc/opinion.md`）：部署高分落在**说完之后的衰减/静音窗**
（`米雅` 有声段内最高 0.604、峰值 0.827 落在 rms=12.8 的静音 chunk；`14次件` 峰值 0.869 落在 rms=15.6），
正负样本在「尾音衰减 + 静音」轴上重叠，训练无法利用音节差异。

管线仍与 `_t2_stream_features_v02.py` 一致（HB-027 逐件流式、HB-028 目录内有 wav）。
**基线 = v0.9 特征集**（v1.0 / v1.1 的特征集不带入）。

Run:  .venv\Scripts\python.exe training\_t2_v10c_features.py
"""
import os
import shutil
import sys
import wave

import numpy as np

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import _t2_stream_features_v02 as sf  # noqa: E402
from openwakeword.utils import AudioFeatures  # noqa: E402

V9 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9")
V10 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.0")
V11 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.1")
V10C = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.0c")
SUBS = ("positive_train", "positive_test", "negative_train", "negative_test")
REPOS = 5
RENEG = 1
POS_KEEP = 0.8          # Q15 第 1 条：正样本窗截到前 0.8 s
RMS_GATE = 120.0        # Q15 第 2 条：24 帧窗原始 RMS 门限

# Q15 第 3 条：真人近音件只作验收集
EXCLUDE_NEG = {
    "negx_tr_1400.wav": "真人近音 爱你老师 → 只作音节窗验收集",
    "negx_tr_1401.wav": "真人近音 雅诗兰黛（峰值 0.822，Q14 已剔除）→ 验收集",
    "negx_tr_1402.wav": "真人近音 米雅（峰值 0.827，Q14 已剔除）→ 验收集",
}

NAMES = {"positive_train": "positive_features_train.npy",
         "positive_test": "positive_features_test.npy",
         "negative_train": "negative_features_train.npy",
         "negative_test": "negative_features_test.npy"}

SRC = {"positive_train": [(V10, "positive_train"), (V11, "positive_train")],
       "positive_test": [(V10, "positive_test"), (V11, "positive_test")],
       "negative_train": [(V10, "negative_train")],
       "negative_test": [(V10, "negative_test")]}


def rms(a):
    return float(np.sqrt(np.mean(a.astype(np.float32) ** 2))) if len(a) else 0.0


def save(data, sub, name):
    """HB-028：训练目录内要留 wav（正样本是截前 0.8 s 后的版本）。"""
    d = os.path.join(V10C, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sf.SR)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())
    return p


def rows_for(sub, positive, F):
    out_rows = []
    kept_files = []
    for base, sub_src in SRC[sub]:
        d = os.path.join(base, sub_src)
        for f in sorted(os.listdir(d)):
            if not f.endswith(".wav"):
                continue
            if not positive and f in EXCLUDE_NEG:
                print(f"  [{sub}] 剔除 {f}：{EXCLUDE_NEG[f]}", flush=True)
                continue
            data = sf.load_wav(os.path.join(d, f))
            if positive:
                data = data[: int(POS_KEEP * sf.SR)]   # Q15 第 1 条
            frames, bounds = sf.stream(F, data)
            M = frames.shape[0]
            spf = (sf.WARMUP * 2 + data.shape[0]) / max(M, 1)
            vr = sf.voiced_range(data, spf) if positive else None
            cands = [b for b in bounds if sf.NFR <= b <= M]
            if positive:
                ws = sf.clip_windows(frames, vr, True, bounds)
                n_drop = 0
            else:
                keep_b = []
                for b in cands:
                    end = int(b * spf) - sf.WARMUP
                    start = int((b - sf.NFR) * spf) - sf.WARMUP
                    seg = data[max(0, start):max(0, end)]
                    if rms(seg) >= RMS_GATE:
                        keep_b.append(b)
                n_drop = len(cands) - len(keep_b)
                ws = [frames[b - sf.NFR:b] for b in keep_b[: sf.MAXW]]
            if not ws:
                print(f"  [{sub}] {f} 无合格窗口（正 {POS_KEEP} s / 负 RMS<{RMS_GATE}）", flush=True)
                continue
            kept_files.append((os.path.basename(d), f, len(ws), n_drop))
            save(data, sub, f)
            out_rows.append((np.stack(ws, axis=0), REPOS if positive else RENEG))
    for (d, f, n, nd) in kept_files:
        print(f"  [{sub}] {d}/{f} 窗口 {n} 个（剔除纯静音窗 {nd}）", flush=True)
    if not out_rows:
        return np.zeros((0, sf.NFR, 96), np.float32)
    rows = [arr for arr, rep in out_rows for _ in range(rep)]
    merged = np.concatenate(rows, axis=0).astype(np.float32)
    print(f"[{sub}] {len(out_rows)} clips -> {merged.shape[0]} rows (rep={REPOS if positive else RENEG})",
          flush=True)
    return merged


def main() -> int:
    os.makedirs(V10C, exist_ok=True)
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
        np.save(os.path.join(V10C, name), merged)
        print(f"[merge] {name}: v0.9 {old.shape[0]} + new {new[sub].shape[0]} -> {merged.shape[0]}", flush=True)

    shutil.copy(os.path.join(V9, "val_fp.npy"), os.path.join(V10C, "val_fp.npy"))
    print("[val_fp] copied from v0.9", flush=True)
    for sub in SUBS:
        n = len([f for f in os.listdir(os.path.join(V10C, sub)) if f.endswith(".wav")])
        print(f"[wavs] {sub}: {n} 件（截前 {POS_KEEP} s / 剔除纯静音窗 / 真人近音不入库）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
