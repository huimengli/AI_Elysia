r"""v0.5 抗干扰后训练数据：把已有样本与既有噪声池按多档 SNR 混合。

需求（用户 2026-11-10 21:1x，见 records/2026-11-10-21-02-16.md 追加节）：
  「将一些噪音和已有的音频样本做混合,然后进行抗干扰的后训练」

做法：
  * 源 clip：真人正/负样本（v0.4 目录里的 posx_tr_10xx / pos_te_10xx / negx_tr_10xx /
    negx_te_10xx）+ v0.3 合成正/负样本抽样 + 既有噪声池（openWakeWord/background/noise）
  * SNR 档位：-5 / 0 / 5 / 10 dB（噪声功率 = 信号功率 / 10^(SNR/20)，随机对齐窗口）
  * 另加「纯噪声窗口」（同等电平、不含语音）作为负样本，强化 FP 抵抗
  * 命名沿用既有前缀并延续编号（posx_tr_11xx / pos_te_11xx / negx_tr_11xx / negx_te_11xx /
    noise_tr_11xx / noise_te_11xx），不新造目录结构
  * 抽样与种子固定（seed=42），可复现；真人正样本全部参与，合成样本按比例抽样

写入 `openWakeWord/output/aili_xiya_v0.4/`（同一套四个标准目录）。

Run:  .venv\Scripts\python.exe _t2_v04_noisy_clips.py
"""
import os
import random
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 16000
V3 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.3")
V4 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.4")
NOISE = os.path.join(ROOT, "openWakeWord", "background", "noise")
SNRS = [-5.0, 0.0, 5.0, 10.0]
SEED = 42

# 抽样规模（真人全量，合成按比例）
POS_TRAIN_SRC = [("v0.4", "posx_tr_1000.wav"), ("v0.4", "posx_tr_1001.wav"),
                ("v0.3", "posx_tr_0500.wav"), ("v0.3", "posx_tr_0501.wav"),
                ("v0.3", "posx_tr_0502.wav"), ("v0.3", "posx_tr_0503.wav"),
                ("v0.3", "posx_tr_0504.wav"), ("v0.3", "posx_tr_0505.wav")]
POS_TEST_SRC = [("v0.4", "pos_te_1000.wav"), ("v0.4", "pos_te_1001.wav"),
                ("v0.3", "pos_te_0100.wav"), ("v0.3", "pos_te_0101.wav"),
                ("v0.3", "pos_te_0102.wav"), ("v0.3", "pos_te_0103.wav")]
NEG_TRAIN_SRC = [("v0.4", f"negx_tr_100{i}.wav") for i in range(6)] + \
                [("v0.3", f"negadv_tr_{i:04d}.wav") for i in (0, 1, 2, 3, 4, 5, 6, 7)]
NEG_TEST_SRC = [("v0.4", f"negx_te_100{i}.wav") for i in range(3)] + \
               [("v0.3", f"negadv_te_{i:03d}.wav") for i in (0, 1, 2, 3, 4, 5, 6, 7)]


def load(p: str) -> np.ndarray:
    with wave.open(p, "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2, p
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)


def path_for(tag: str, name: str) -> str:
    base = V4 if tag == "v0.4" else V3
    sub = {"posx_tr": "positive_train", "pos_te": "positive_test",
           "negx_tr": "negative_train", "negx_te": "negative_test",
           "negadv_tr": "negative_train", "negadv_te": "negative_test",
           "noise_tr": "negative_train", "noise_te": "negative_test"}[name.split("_")[0] + "_" + name.split("_")[1]]
    return os.path.join(base, sub, name)


def save(data: np.ndarray, sub: str, name: str) -> str:
    d = os.path.join(V4, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())
    return p


def mix(sig: np.ndarray, noise_files: list, snr: float, rng) -> np.ndarray:
    """Mix signal with a random noise window at the requested SNR (dB)."""
    n = None
    total = 0
    while n is None or total < len(sig):
        f = rng.choice(noise_files)
        x = load(f)
        n = x if n is None else np.concatenate([n, x])
        total += len(x)
    start = rng.randint(0, max(1, len(n) - len(sig)))
    nz = n[start:start + len(sig)]
    sp = float(np.sqrt(np.mean(sig ** 2)) + 1.0)
    npw = float(np.sqrt(np.mean(nz ** 2)) + 1.0)
    gain = sp / (npw * 10 ** (snr / 20.0))
    return sig + nz * gain


def main() -> int:
    rng = random.Random(SEED)
    noise_files = [os.path.join(NOISE, f) for f in sorted(os.listdir(NOISE)) if f.endswith(".wav")]
    print(f"noise pool: {len(noise_files)} files, SNR={SNRS}, seed={SEED}", flush=True)
    counts = [0]
    ref = float(np.sqrt(np.mean(load(path_for("v0.4", "posx_tr_1001.wav")) ** 2)))

    def run(srcs, sub, prefix, start_idx):
        idx = start_idx
        for tag, name in srcs:
            sig = load(path_for(tag, name))
            for snr in SNRS:
                out = mix(sig, noise_files, snr, rng)
                p = save(out, sub, f"{prefix}_{idx:04d}.wav")
                sr_ = float(np.sqrt(np.mean(sig ** 2)))
                nr_ = float(np.sqrt(np.mean(out ** 2)))
                print(f"[{sub}] {prefix}_{idx:04d} <- {tag}/{name} SNR={snr:+.0f}dB "
                      f"sigRMS={sr_:.0f} mixRMS={nr_:.0f} dur={len(sig)/SR:.2f}s", flush=True)
                idx += 1
                counts[0] += 1
        return idx

    run(POS_TRAIN_SRC, "positive_train", "posx_tr", 1100)
    run(POS_TEST_SRC, "positive_test", "pos_te", 1100)
    run(NEG_TRAIN_SRC, "negative_train", "negx_tr", 1100)
    run(NEG_TEST_SRC, "negative_test", "negx_te", 1100)

    # 纯噪声窗口（同等电平、不含语音）作为 FP 抵抗负样本：
    # 噪声 RMS 定标为「真人正样本 RMS / 10^(SNR/20)」，即与 SNR 档位同电平但没有语音
    for sub, prefix, start in (("negative_train", "noise_tr", 1100), ("negative_test", "noise_te", 1100)):
        for k, snr in enumerate(SNRS):
            idx = start + k
            target = ref / 10 ** (snr / 20.0)
            nz = mix(np.zeros(int(SR * 2.0), np.float32), noise_files, 0.0, rng)
            cur = float(np.sqrt(np.mean(nz ** 2))) + 1e-6
            out = nz * (target / cur)
            p = save(out, sub, f"{prefix}_{idx:04d}.wav")
            print(f"[{sub}] {prefix}_{idx:04d} 纯噪声 SNR档={snr:+.0f}dB 目标RMS={target:.0f} "
                  f"实际RMS={np.sqrt(np.mean(out ** 2)):.0f} -> {os.path.basename(p)}", flush=True)
            counts[0] += 1

    print(f"total noisy clips written: {counts[0]} -> {V4}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
