r"""v0.4 数据第一步：把真人录音（用户 2026-11-10 提供的 录音.m4a）切成训练/验收 clip。

标注依据 = faster-whisper 词级时间戳（ASR 确认的「爱莉希雅」）+ 逐 0.5 s 响度 + v0.3 分数。
命名沿用既有约定（`posx_tr_####.wav` / `pos_te_####.wav` / `negx_tr_####.wav` / `negx_te_####.wav`），
不新造目录结构（AGENTS 第 0 节）。真人正样本 2 条入训练、2 条入验收留出（逐 clip 不重叠）。
高分但 ASR 未确认的窗口（27.5-30.0、31.7-32.6）标为「未标注」，本轮不入库，等 need_user.md Q8 用户确认。

Run:
  .venv\Scripts\python.exe _t2_v04_real_clips.py "<录音.m4a 路径>"
"""
import os
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SR = 16000
CHUNK = 1280
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.4")

# ASR (word timestamps) 确认的呼唤窗口
POS_WINDOWS = [(1.20, 2.60), (2.70, 4.70), (30.40, 31.90), (33.00, 34.50)]
POS_TRAIN = [POS_WINDOWS[0], POS_WINDOWS[1]]
POS_TEST = [POS_WINDOWS[2], POS_WINDOWS[3]]

# 高分但无 ASR 确认：本轮不入库（Q8 等确认）
AMBIGUOUS = [(27.0, 30.2), (31.7, 32.7)]

# 有声且无呼唤的真人片段 -> 真人负样本（同音色，内容不含唤醒词）
# 每个窗口都严格避开 4 个 ASR 确认的呼唤区间（逐段核对 seg3.log 的 0.5s 响度剖面）
NEG_VOICED = [(5.5, 8.0), (8.0, 10.5), (11.0, 13.5), (14.0, 16.5), (16.5, 19.0),
              (19.5, 22.0), (22.5, 25.0), (25.0, 27.5), (34.5, 36.0)]

# 明显安静的片段 -> 静音负样本（1.0–2.0 s，同样严格避开呼唤区间）
NEG_QUIET = [(0.0, 1.2), (4.7, 5.5), (7.0, 8.0), (9.5, 11.0), (12.5, 14.0),
             (15.5, 16.5), (18.0, 19.5), (21.0, 22.5), (26.0, 27.5), (29.3, 30.4)]


def decode(path: str) -> np.ndarray:
    import av

    res = av.AudioResampler(format="s16", layout="mono", rate=SR)
    frames = []
    with av.open(path) as c:
        st = c.streams.audio[0]
        for f in c.decode(st):
            for r in res.resample(f):
                frames.append(r.to_ndarray().reshape(-1))
    return np.concatenate(frames).astype(np.int16)


def save(data: np.ndarray, sub: str, name: str) -> str:
    d = os.path.join(OUT, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return p


def score_windows(audio: np.ndarray, model) -> list:
    """v0.3 max score over the window (streaming, chunk-aligned)."""
    model.reset()
    best = 0.0
    for i in range(0, len(audio) - CHUNK, CHUNK):
        s = model.predict(audio[i:i + CHUNK])
        best = max(best, max(s.values()))
    return best


def main() -> int:
    src = sys.argv[1]
    audio = decode(src)
    print(f"decoded {len(audio)/SR:.2f} s from {src}")

    import openwakeword

    m = openwakeword.Model(
        wakeword_models=[os.path.join(ROOT, "openWakeWord", "output",
                                     "aili_xiya_v0.3", "aili_xiya_v0.3.onnx")],
        inference_framework="onnx")

    total = 0
    for idx, (a, b) in enumerate(POS_TRAIN):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "positive_train", f"posx_tr_10{idx:02d}.wav")
        print(f"POS-TRAIN {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} "
              f"rms={np.sqrt(np.mean(seg.astype(np.float32)**2)):.0f} v0.3max={score_windows(seg, m):.3f} -> {p}")
        total += 1
    for idx, (a, b) in enumerate(POS_TEST):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "positive_test", f"pos_te_10{idx:02d}.wav")
        print(f"POS-TEST  {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} "
              f"rms={np.sqrt(np.mean(seg.astype(np.float32)**2)):.0f} v0.3max={score_windows(seg, m):.3f} -> {p}")
        total += 1

    ntr = 0
    for a, b in NEG_VOICED[:6]:
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "negative_train", f"negx_tr_10{ntr:02d}.wav")
        print(f"NEG-VOICED(train) {a:.2f}-{b:.2f}s v0.3max={score_windows(seg, m):.3f} -> {p}")
        ntr += 1
        total += 1
    nte = 0
    for a, b in NEG_VOICED[6:]:
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "negative_test", f"negx_te_10{nte:02d}.wav")
        print(f"NEG-VOICED(test)  {a:.2f}-{b:.2f}s v0.3max={score_windows(seg, m):.3f} -> {p}")
        nte += 1
        total += 1

    for idx, (a, b) in enumerate(NEG_QUIET[:3]):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "negative_train", f"noise_tr_10{idx:02d}.wav")
        print(f"NEG-QUIET(train)  {a:.2f}-{b:.2f}s v0.3max={score_windows(seg, m):.3f} -> {p}")
        total += 1
    for idx, (a, b) in enumerate(NEG_QUIET[3:]):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "negative_test", f"noise_te_10{idx:02d}.wav")
        print(f"NEG-QUIET(test)   {a:.2f}-{b:.2f}s v0.3max={score_windows(seg, m):.3f} -> {p}")
        total += 1

    print(f"total clips written: {total} -> {OUT}")
    print("未标注（不入库，等 Q8 确认）:", AMBIGUOUS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
