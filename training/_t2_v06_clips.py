r"""v0.6 数据第一步：按用户确认的「13 次呼唤」重标真人录音（录音.m4a，36.12 s）。

需求（用户 2026-11-10 22:17，见 records/2026-11-10-22-17-39.md）：
  「这段录音总计 13 次, 没有噪音,平均2-3秒一次, 补录的活明天弄」

即：本录音的 13 次呼唤**全部是正样本**，没有任何真人负样本（用户明确「没有噪音」）。
上一批（21-02-16）把 8 段真呼唤当真人负样本入库 = 教模型拒绝唤醒词，本批重标纠正。

呼唤位置由 `aili_xiya_v0.3.onnx` 逐 chunk 分数的局部峰定位（`.tmp/probe_seg5.py` 检出恰好
13 个峰，间隔 2.0–3.9 s，与用户说的「平均 2-3 秒一次」吻合）；每个窗口取 [峰-0.5, 峰+1.0]
（1.5 s），逐窗口核对不与其它窗口重叠。负样本只取**呼唤窗口之外的纯安静间隙**（静音负样本），
不产出真人负样本（等明日补录，need_user.md Q9）。

命名沿用既有前缀并延续编号（posx_tr_12xx / pos_te_12xx / noise_tr_12xx / noise_te_12xx），
不新造目录结构（AGENTS 第 0 节）。写入 `openWakeWord/output/aili_xiya_v0.6/`。

Run:  .venv\Scripts\python.exe _t2_v06_clips.py "<录音.m4a 路径>"
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
OUT = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.6")

# v0.3 分数局部峰（probe_seg5.log，13 个）→ 呼唤窗口 [峰-0.5, 峰+1.0]
PEAKS = [0.56, 3.44, 7.36, 9.36, 12.24, 15.04, 18.40, 20.72, 23.28, 26.00,
         29.68, 31.76, 34.40]
POS_TRAIN = [(p - 0.5, p + 1.0) for p in PEAKS[:10]]      # 10 条入训练
POS_TEST = [(p - 0.5, p + 1.0) for p in PEAKS[10:]]       # 3 条入验收留出

# 纯安静间隙 → 静音负样本。**不能用「两峰之间」当安静**：呼唤约 2.5 s 一次，两峰之间
# 常含呼唤的起音/尾音（实测 `noise_tr_1200`(1.70-2.80) 的 v0.3 窗口最高分 0.822，
# `noise_tr_1203`(13.40-14.40) 0.816）。所以安静窗由 v0.3 平滑分数的**低谷区**程序化确定：
# 只在 0.32 s 平滑分数 < 0.25 的连续区（≥0.5 s）内取窗，并留 0.15 s 边缘余量。
NEG_QUIET_TRAIN = None   # 运行时计算
NEG_QUIET_TEST = None
LOW_SCORE = 0.25
MIN_LOW_LEN = 0.8  # 实测：呼唤 2.5 s 一轮，本录音剔除呼唤窗口后没有 ≥0.8 s 的干净低分区


def trough_windows(scores: list, fps: float, lo: float, min_len: float) -> list:
    """连续低分区 [start, end]（秒），已留 0.15 s 边缘余量。"""
    sm = np.convolve(np.array(scores), np.ones(4) / 4, mode="same")
    regions = []
    i = 0
    n = len(sm)
    while i < n:
        if sm[i] < lo:
            j = i
            while j < n and sm[j] < lo:
                j += 1
            span = (i / fps, j / fps)
            if span[1] - span[0] >= min_len:
                regions.append((span[0] + 0.15, span[1] - 0.15))
            i = j
        i += 1
    return [r for r in regions if r[1] > r[0]]



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


def score_windows(audio: np.ndarray, model) -> float:
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
    dur = len(audio) / SR
    print(f"decoded {dur:.2f} s from {src}")

    # 逐窗口重叠校验（呼唤窗口之间）
    pos_sorted = sorted(POS_TRAIN + POS_TEST)
    for a, b in pos_sorted:
        assert 0 <= a < b <= dur, (a, b)
    for i in range(len(pos_sorted) - 1):
        w1 = pos_sorted[i]
        w2 = pos_sorted[i + 1]
        assert w1[1] <= w2[0], f"呼唤窗口重叠: {w1} vs {w2}"

    import openwakeword

    m = openwakeword.Model(
        wakeword_models=[os.path.join(ROOT, "openWakeWord", "output",
                                     "aili_xiya_v0.3", "aili_xiya_v0.3.onnx")],
        inference_framework="onnx")

    # 全文件逐 chunk 分数（12.5 chunk/s）→ 低分区
    m.reset()
    scores = []
    for i in range(0, len(audio) - CHUNK, CHUNK):
        scores.append(max(m.predict(audio[i:i + CHUNK]).values()))
    regions = trough_windows(scores, SR / CHUNK, LOW_SCORE, MIN_LOW_LEN)
    # 低分区必须剔除呼唤窗口（低分常紧跟在呼唤尾音之后，如 8.07-8.41 落在 6.86-8.36 窗口内）
    allpos = sorted(POS_TRAIN + POS_TEST)
    cut = []
    for a, b in regions:
        cur = a
        for p, q in allpos:
            if q <= cur or p >= b:
                continue
            if p > cur:
                cut.append((cur, min(p, b)))
            cur = max(cur, q)
        if b > cur:
            cut.append((cur, b))
    regions = [(x, y) for x, y in cut if y - x >= MIN_LOW_LEN]
    print(f"低分区（平滑分数 < {LOW_SCORE}，≥{MIN_LOW_LEN}s，已剔除呼唤窗口）共 {len(regions)} 段:")
    for a, b in regions:
        print(f"  {a:.2f}-{b:.2f} len={b-a:.2f}s")

    allpos = sorted(POS_TRAIN + POS_TEST)
    for a, b in regions:
        for p, q in allpos:
            assert b <= p or a >= q, f"低分窗与呼唤窗口重叠: {(a, b)} vs {(p, q)}"

    NEG_QUIET_TRAIN = [r for r in regions if r[0] < 27.0]
    NEG_QUIET_TEST = [r for r in regions if r[0] >= 27.0]
    print(f"静音负样本: train={len(NEG_QUIET_TRAIN)} test={len(NEG_QUIET_TEST)}")

    total = 0
    for idx, (a, b) in enumerate(POS_TRAIN):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "positive_train", f"posx_tr_12{idx:02d}.wav")
        print(f"POS-TRAIN {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} "
              f"rms={np.sqrt(np.mean(seg.astype(np.float32)**2)):.0f} "
              f"v0.3max={score_windows(seg, m):.3f} -> {p}", flush=True)
        total += 1
    for idx, (a, b) in enumerate(POS_TEST):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "positive_test", f"pos_te_12{idx:02d}.wav")
        print(f"POS-TEST  {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} "
              f"rms={np.sqrt(np.mean(seg.astype(np.float32)**2)):.0f} "
              f"v0.3max={score_windows(seg, m):.3f} -> {p}", flush=True)
        total += 1

    for idx, (a, b) in enumerate(NEG_QUIET_TRAIN):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "negative_train", f"noise_tr_12{idx:02d}.wav")
        print(f"NEG-QUIET(train) {a:.2f}-{b:.2f}s "
              f"v0.3max={score_windows(seg, m):.3f} -> {p}", flush=True)
        total += 1
    for idx, (a, b) in enumerate(NEG_QUIET_TEST):
        seg = audio[int(a * SR):int(b * SR)]
        p = save(seg, "negative_test", f"noise_te_12{idx:02d}.wav")
        print(f"NEG-QUIET(test)  {a:.2f}-{b:.2f}s "
              f"v0.3max={score_windows(seg, m):.3f} -> {p}", flush=True)
        total += 1

    print(f"total clips written: {total} -> {OUT}", flush=True)
    print("真人负样本：本录音无（用户确认无噪音），等明日补录（need_user.md Q9）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
