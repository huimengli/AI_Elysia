r"""诊断：`米雅` 在 aili_xiya_v0.9 上为什么拿到 0.827（用户 2026-11-12 21:39 的质疑）。

用户判断：「按理来讲 米雅 和 爱莉希雅 差别很大才对」—— 语音差别大就不该拿到与真唤醒同量级的分数。
本脚本把逐 1280-sample chunk（与线上同一口径、1 s 零填充预热、24 帧感受野）的分数曲线打出来，
定位峰值落在哪个时间窗，再按 RMS 切音节，把「峰值窗 = 哪个音节」与真唤醒件的峰值窗对齐比较；
并做两个切片段实验（`米雅` 的尾音节 / `爱莉希雅` 的尾音节 `雅`）来验证「模型是否被尾音节 `yǎ` 主导」。

Run:  $env:MPLCONFIGDIR='.tmp\mpl'; .venv\Scripts\python.exe training\_t2_miya_score_curve.py
"""
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
SR = 16000
CHUNK = 1280
FPS = SR / CHUNK          # 每 chunk 0.08 s
REC = r"C:\Users\楼听\Documents\录音"
SCORER = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9", "aili_xiya_v0.9.onnx")
NAME = "aili_xiya_v0.9"

FILES = [
    ("米雅", "'米雅'.m4a"),
    ("雅诗兰黛", "'雅诗兰黛'.m4a"),
    ("爱你老师", "'爱你老师'.m4a"),
    ("希雅老师(基线)", "'希雅老师'.m4a"),
    ("爱莉雅(基线)", "'爱莉雅'.m4a"),
    ("米希雅(基线)", "'米希雅'.m4a"),
    ("14次干净呼唤", "14次 几乎干净的'爱莉希雅'.m4a"),
]


def decode(path):
    import av
    res = av.AudioResampler(format="s16", layout="mono", rate=SR)
    out = []
    with av.open(path) as c:
        for f in c.decode(c.streams.audio[0]):
            for r in res.resample(f):
                out.append(r.to_ndarray().reshape(-1))
    return np.concatenate(out).astype(np.int16)


def rms(a):
    return float(np.sqrt(np.mean(a.astype(np.float32) ** 2)))


def series(audio, n=3):
    """逐 chunk 分数，n 个**独立新建实例**（HB-032 播种独立性）。"""
    import gc
    import openwakeword
    out = []
    for _ in range(n):
        m = openwakeword.Model(wakeword_models=[SCORER], inference_framework="onnx", ncpu=1)
        out.append([float(m.predict(audio[i:i + CHUNK]).get(NAME, 0.0))
                    for i in range(0, max(1, len(audio) - CHUNK), CHUNK)])
        del m
        gc.collect()
    return out


def voiced_regions(audio, thr_rms=120.0, min_len=0.24):
    """按 0.08 s 粒度的 RMS 有声段（近似音节边界）：>=thr_rms 的连续段。"""
    n = len(audio) // CHUNK
    r = [rms(audio[i * CHUNK:(i + 1) * CHUNK]) for i in range(n)]
    segs, i = [], 0
    while i < n:
        if r[i] >= thr_rms:
            j = i
            while j < n and r[j] >= thr_rms:
                j += 1
            if (j - i) * 0.08 >= min_len:
                segs.append((i, j, max(r[i:j])))
            i = j
        else:
            i += 1
    return r, segs


def main() -> int:
    for label, fn in FILES:
        p = os.path.join(REC, fn)
        if not os.path.exists(p):
            print(f"[跳过] {label} 找不到 {fn}")
            continue
        audio = decode(p)
        sc = series(audio, 3)
        r, segs = voiced_regions(audio)
        peak3 = [max(s) for s in sc]
        k = int(np.argmax(sc[0]))
        print(f"\n### {label}（{len(audio)/SR:.2f} s）3 实例峰值 = "
              f"{round(peak3[0],3)}/{round(peak3[1],3)}/{round(peak3[2],3)}，"
              f"最高 chunk #{k} = {k*0.08:.2f}-{(k+1)*0.08:.2f} s，该 chunk rms={round(r[k],1)}")
        # 逐 chunk 分数曲线（只打有声段附近，避免刷屏）
        lo = max(0, k - 12)
        hi = min(len(sc[0]), k + 12)
        print("  chunk  时间      rms     3 实例分数（>=0.70 标 *）")
        for i in range(lo, hi):
            star = "*" if sc[0][i] >= 0.70 else " "
            print(f"  {i:5d}  {i*0.08:5.2f}s  {r[i]:6.1f}   "
                  f"{sc[0][i]:.3f}{star} {sc[1][i]:.3f} {sc[2][i]:.3f}")
        print("  有声段（RMS>=120 连续段，近似音节）：")
        for (a, b, mx) in segs:
            print(f"    {a*0.08:5.2f}-{b*0.08:5.2f}s  len={(b-a)*0.08:.2f}s  rms峰值={mx:.0f}  "
                  f"该段内最高分={max(sc[0][a:b]):.3f}" if b > a else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
