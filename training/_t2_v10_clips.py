r"""v1.0 数据第一步：2026-11-12 17:10-17:22 的 14 件真人补录切成 14xx clip（records/2026-11-12-17-22-40.md）。

用户补录（文件名即真值，含单引号是真实字符）：
- `14次 几乎干净的'爱莉希雅'.m4a`（40.89 s，14 次呼唤）→ **正样本**
- `带键盘噪音的 4次 '爱莉希雅'.m4a`（14.97 s，4 次呼唤）→ **带噪正样本**
- `带轻音乐的'爱莉希雅'.m4a` / `2` / `3`、`带歌声的'爱莉希雅'.m4a` / `2` / `3`（各 1 次呼唤）→ **带噪正样本**
- `'爱你老师'.m4a` / `'雅诗兰黛'.m4a` / `'米雅'.m4a`（真人近音，不含唤醒词，在 need_audio.md §5 允许清单内）→ **负样本**
- `'天猫精灵'.m4a`（竞品唤醒词真人句，v0.9 峰值 0.759/0.741/0.742）→ **负样本**
- `'我没听清,请再说一遍'.m4a`（应答语，不含唤醒词）→ **负样本**
- `机械键盘噪音.m4a`（16.53 s，v0.9 峰值 0.816/0.844/0.814 —— 键盘敲击确实会触发）→ 切低分窗入库
- `环境音.m4a`（30.85 s，rms=0.0005 的安静基线）→ 切低分窗入库

规则沿用既有约定（不新造目录/前缀，AGENTS §0）：
- 呼唤窗口由 `aili_xiya_v0.9.onnx` 逐 chunk 分数定位（与线上同一口径：1280 chunk、阈值 0.7、2 s 冷却），
  窗口取 [检出时刻-0.5, 检出时刻+1.0]（1.5 s），窗口之间必须不重叠。
- **真人件不按峰值剔除**（峰值只作验收证据；v0.4/v0.5 的教训是「把真呼唤当负样本」，不是「峰值高就剔除」）。
- 噪声/环境音只取平滑分数 <0.25 的连续低分区（≥1.5 s，留 0.15 s 边缘余量）。

Run:  .venv\Scripts\python.exe training\_t2_v10_clips.py
"""
import os
import sys
import wave

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
SR = 16000
CHUNK = 1280
THR = 0.7
GAP = 2.0
REC = r"C:\Users\楼听\Documents\录音"
V10 = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v1.0")
SCORER = os.path.join(ROOT, "openWakeWord", "output", "aili_xiya_v0.9", "aili_xiya_v0.9.onnx")

# 多呼唤件：(标签, 文件名, 期望次数, train 前几条)
MULTI = [("14次干净", "14次 几乎干净的'爱莉希雅'.m4a", 14, 11),
         ("键盘噪音4次", "带键盘噪音的 4次 '爱莉希雅'.m4a", 4, 4)]
# 单呼唤件：(标签, 文件名, split)
SINGLE = [("带轻音乐1", "带轻音乐的'爱莉希雅'.m4a", "train"),
          ("带轻音乐2", "带轻音乐的'爱莉希雅'2.m4a", "train"),
          ("带轻音乐3", "带轻音乐的'爱莉希雅'3.m4a", "train"),
          ("带歌声1", "带歌声的'爱莉希雅'.m4a", "train"),
          ("带歌声2", "带歌声的'爱莉希雅'2.m4a", "test"),
          ("带歌声3", "带歌声的'爱莉希雅'3.m4a", "test")]
# 真人负样本（不含唤醒词，文件名即真值，整件入库，不按峰值剔除）
REAL_NEG = [("近音 爱你老师", "'爱你老师'.m4a", "train"),
            ("近音 雅诗兰黛", "'雅诗兰黛'.m4a", "train"),
            ("近音 米雅", "'米雅'.m4a", "train"),
            ("竞品唤醒 天猫精灵", "'天猫精灵'.m4a", "train"),
            ("应答语 我没听清", "'我没听清,请再说一遍'.m4a", "test")]
NOISE_FILES = [("机械键盘噪音", "机械键盘噪音.m4a"),
               ("环境音（安静房间）", "环境音.m4a")]

POS_TRAIN_ID = [1400]
POS_TEST_ID = [1400]
NEG_TRAIN_ID = [1400]
NEG_TEST_ID = [1400]
LOW_SCORE = 0.25
MIN_LOW_LEN = 1.5


def decode(path):
    import av
    res = av.AudioResampler(format="s16", layout="mono", rate=SR)
    out = []
    with av.open(path) as c:
        for f in c.decode(c.streams.audio[0]):
            for r in res.resample(f):
                out.append(r.to_ndarray().reshape(-1))
    return np.concatenate(out).astype(np.int16)


def save(data, sub, name):
    d = os.path.join(V10, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(data, -32768, 32767).astype(np.int16).tobytes())
    return p


def rms(a):
    return float(np.sqrt(np.mean(a.astype(np.float32) ** 2)))


def main() -> int:
    import openwakeword
    m = openwakeword.Model(wakeword_models=[SCORER], inference_framework="onnx")

    def scores(audio):
        m.reset()
        return [float(m.predict(audio[i:i + CHUNK]).get("aili_xiya_v0.9", 0.0))
                for i in range(0, max(1, len(audio) - CHUNK), CHUNK)]

    fps = SR / CHUNK

    def trough_windows(sc):
        sm = np.convolve(np.array(sc), np.ones(4) / 4, mode="same")
        regions, i, n = [], 0, len(sm)
        while i < n:
            if sm[i] < LOW_SCORE:
                j = i
                while j < n and sm[j] < LOW_SCORE:
                    j += 1
                span = (i / fps, j / fps)
                if span[1] - span[0] >= MIN_LOW_LEN:
                    regions.append((span[0] + 0.15, span[1] - 0.15))
                i = j
            i += 1
        return [r for r in regions if r[1] > r[0]]

    total = 0
    # 1) 多呼唤件：检出时刻定位窗口
    for tag, fname, expect, n_train in MULTI:
        audio = decode(os.path.join(REC, fname))
        sc = scores(audio)
        evs = []
        for i, s in enumerate(sc):
            if s >= THR:
                t = i / fps
                if evs and (t - evs[-1]) < GAP:
                    continue
                evs.append(t)
        windows = [(t - 0.5, t + 1.0) for t in evs]
        windows.sort()
        # 检出间隔已 >=GAP(2.0 s)，窗口 1.5 s，故 [t-0.5, t+1.0] 必然不重叠；这里显式校验非重叠
        ok = all(w1[1] <= w2[0] for w1, w2 in zip(windows[:-1], windows[1:]))
        print(f"\n{tag} {len(audio)/SR:.2f} s：检出 {len(evs)} 次（期望 {expect}），窗口不重叠={ok}", flush=True)
        for idx, (a, b) in enumerate(windows):
            a = max(0.0, a)
            b = min(len(audio) / SR, b)
            seg = audio[int(a * SR):int(b * SR)]
            split = "train" if idx < n_train else "test"
            if split == "train":
                name = f"posx_tr_{POS_TRAIN_ID[0]}"
                POS_TRAIN_ID[0] += 1
            else:
                name = f"pos_te_{POS_TEST_ID[0]}"
                POS_TEST_ID[0] += 1
            p = save(seg, "positive_train" if split == "train" else "positive_test", name + ".wav")
            wmax = max(scores(seg))
            print(f"  POS({split}) {tag} #{idx} {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} "
                  f"rms={rms(seg):.0f} v0.9max={wmax:.3f} -> {name}.wav", flush=True)
            total += 1

    # 2) 单呼唤件：峰值窗口
    for tag, fname, split in SINGLE:
        audio = decode(os.path.join(REC, fname))
        sc = scores(audio)
        if not sc:
            print(f"  跳过 {tag}（过短）", flush=True)
            continue
        t = sc.index(max(sc)) / fps
        a, b = max(0.0, t - 0.5), min(len(audio) / SR, t + 1.0)
        seg = audio[int(a * SR):int(b * SR)]
        if split == "train":
            name = f"posx_tr_{POS_TRAIN_ID[0]}"
            POS_TRAIN_ID[0] += 1
        else:
            name = f"pos_te_{POS_TEST_ID[0]}"
            POS_TEST_ID[0] += 1
        p = save(seg, "positive_train" if split == "train" else "positive_test", name + ".wav")
        print(f"  POS({split}) {tag} {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} rms={rms(seg):.0f} "
              f"v0.9max={max(scores(seg)):.3f} -> {name}.wav", flush=True)
        total += 1

    # 3) 真人负样本：整件入库
    for tag, fname, split in REAL_NEG:
        audio = decode(os.path.join(REC, fname))
        if split == "train":
            name = f"negx_tr_{NEG_TRAIN_ID[0]}"
            NEG_TRAIN_ID[0] += 1
        else:
            name = f"negx_te_{NEG_TEST_ID[0]}"
            NEG_TEST_ID[0] += 1
        p = save(audio, "negative_train" if split == "train" else "negative_test", name + ".wav")
        sc = scores(audio)
        n7 = sum(1 for s in sc if s >= THR)
        print(f"  NEG-REAL({split}) {tag} {len(audio)/SR:.2f} s 峰值 {max(sc):.3f}（>=0.7 chunk {n7}）"
              f" rms={rms(audio):.0f} -> {name}.wav", flush=True)
        total += 1

    # 4) 噪声/环境音：低分窗
    for tag, fname in NOISE_FILES:
        audio = decode(os.path.join(REC, fname))
        sc = scores(audio)
        wins = trough_windows(sc)
        print(f"\n{tag} {len(audio)/SR:.2f} s 低分窗（平滑 <{LOW_SCORE}，>= {MIN_LOW_LEN} s）{len(wins)} 段", flush=True)
        for idx, (a, b) in enumerate(wins[:6]):
            split = "train" if idx < 4 else "test"
            if split == "train":
                name = f"noise_tr_{NEG_TRAIN_ID[0]}"
                NEG_TRAIN_ID[0] += 1
            else:
                name = f"noise_te_{NEG_TEST_ID[0]}"
                NEG_TEST_ID[0] += 1
            seg = audio[int(a * SR):int(b * SR)]
            p = save(seg, "negative_train" if split == "train" else "negative_test", name + ".wav")
            print(f"  NEG-NOISE({split}) {a:.2f}-{b:.2f}s dur={len(seg)/SR:.2f} "
                  f"峰值 {max(scores(seg)):.3f} rms={rms(seg):.0f} -> {name}.wav", flush=True)
            total += 1

    print(f"\ntotal clips written: {total} -> {V10}", flush=True)
    print(f"posx_tr 用号 {POS_TRAIN_ID[0]} / pos_te {POS_TEST_ID[0]} / negx_tr+noise_tr {NEG_TRAIN_ID[0]} / "
          f"negx_te+noise_te {NEG_TEST_ID[0]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
