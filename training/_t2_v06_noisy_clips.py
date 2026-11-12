r"""v0.6 抗干扰后训练数据（用户 2026-11-10 21:1x 追加需求，方向在本批纠正）。

需求原话（records/2026-11-10-21-02-16.md 追加节）：
  「将一些噪音和已有的音频样本做混合,然后进行抗干扰的后训练」

上一批（v0.5）的方向错误：被混合的 `negx_*` 其实是真人呼唤（用户 22:17 确认「13 次、没有噪音」），
等于把带噪**呼唤**当负样本训练。本批：
  * 混合源 = 13 条真人呼唤（`posx_tr_1200-1209` / `pos_te_1200-1202`）→ 全部写入 positive_*
  * SNR 档位 -5 / 0 / 5 / 10 dB，噪声池 `openWakeWord/background/noise`（24 文件），seed 42
  * 纯噪声窗口（同等电平、不含语音）作 FP 抵抗负样本，电平按真呼唤 RMS 的 10^(SNR/20) 定标
  * 命名延续既有前缀与编号（posx_tr_1210.. / pos_te_1210.. / noise_tr_1210.. / noise_te_1210..）
  * 本录音**不产出真人负样本**（用户确认无噪音），真人负样本等明日补录（need_user.md Q9）

写入 `openWakeWord/output/aili_xiya_v0.6/`（同一套四个标准目录）。

Run:  .venv\Scripts\python.exe _t2_v06_noisy_clips.py
"""
import os
import random
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 16000
V6 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.6")
NOISE = os.path.join(ROOT, "openWakeWord", "background", "noise")
SNRS = [-5.0, 0.0, 5.0, 10.0]
SEED = 42

POS_TRAIN_SRC = [f"posx_tr_12{i:02d}.wav" for i in range(10)]
POS_TEST_SRC = [f"pos_te_12{i:02d}.wav" for i in range(3)]


def load(p: str) -> np.ndarray:
    with wave.open(p, "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2, p
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)


def save(data: np.ndarray, sub: str, name: str) -> str:
    d = os.path.join(V6, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())
    return p


def mix(sig: np.ndarray, noise_files: list, snr: float, rng) -> np.ndarray:
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
    ref = float(np.sqrt(np.mean(load(os.path.join(V6, "positive_train", "posx_tr_1201.wav")) ** 2)))

    def run(names, sub, prefix, start_idx):
        idx = start_idx
        for name in names:
            sig = load(os.path.join(V6, sub, name))
            for snr in SNRS:
                out = mix(sig, noise_files, snr, rng)
                p = save(out, sub, f"{prefix}_{idx:04d}.wav")
                sr_ = float(np.sqrt(np.mean(sig ** 2)))
                nr_ = float(np.sqrt(np.mean(out ** 2)))
                print(f"[{sub}] {prefix}_{idx:04d} <- {name} SNR={snr:+.0f}dB "
                      f"sigRMS={sr_:.0f} mixRMS={nr_:.0f} dur={len(sig)/SR:.2f}s", flush=True)
                idx += 1
                counts[0] += 1
        return idx

    run(POS_TRAIN_SRC, "positive_train", "posx_tr", 1210)
    run(POS_TEST_SRC, "positive_test", "pos_te", 1210)

    # 纯噪声窗口（同等电平、不含语音）作 FP 抵抗负样本
    for sub, prefix, start in (("negative_train", "noise_tr", 1210), ("negative_test", "noise_te", 1210)):
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

    print(f"total noisy clips written: {counts[0]} -> {V6}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
