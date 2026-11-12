r"""新补录音频可用性探针（2026-11-12 17:22 批次，records/2026-11-12-17-22-40.md）。

零截图；只读 `C:\Users\楼听\Documents\录音`。逐件解码报时长/rms，再用与线上完全一致的部署管线
（1280 chunk 逐块、检出后 reset、冷却 GAP s）在指定模型上打分；边界件按 HB-032 做 n 次独立 Model
实例峰值复测。**单探针串行**（并发 4 个会在 `_streaming_melspectrogram` 触发 MemoryError）。

Run:
  .venv\Scripts\python.exe training/_t2_newaudio_probe.py aili_xiya_v0.9 aili_xiya_v0.6
阈值用环境变量 WTHR（默认 0.7），复测次数 NINST（默认 3）。

期望（按文件名即真值）：
  正样本 14次 几乎干净的'爱莉希雅' = 14 次；带键盘噪音的 4次 = 4 次；带轻音乐/歌声 6 件各 1 次
  负样本 爱你老师 / 雅诗兰黛 / 米雅 / 天猫精灵 / 我没听清 = 0
  噪声 机械键盘噪音 / 环境音 = 0（环境音判据 ≤1）
"""
import os
import sys

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
OUT = os.path.join(ROOT, "openWakeWord", "output")
REC = r"C:\Users\楼听\Documents\录音"
SR = 16000
CHUNK = 1280
THR = float(os.environ.get("WTHR", "0.7"))
GAP = 2.0
NINST = int(os.environ.get("NINST", "3"))

# 新补录（2026-11-12 17:10-17:22），name -> (文件名, 期望检出次数)
NEW_POS = [
    ("14次干净呼唤", "14次 几乎干净的'爱莉希雅'.m4a", 14),
    ("键盘噪音4次呼唤", "带键盘噪音的 4次 '爱莉希雅'.m4a", 4),
    ("带轻音乐1", "带轻音乐的'爱莉希雅'.m4a", 1),
    ("带轻音乐2", "带轻音乐的'爱莉希雅'2.m4a", 1),
    ("带轻音乐3", "带轻音乐的'爱莉希雅'3.m4a", 1),
    ("带歌声1", "带歌声的'爱莉希雅'.m4a", 1),
    ("带歌声2", "带歌声的'爱莉希雅'2.m4a", 1),
    ("带歌声3", "带歌声的'爱莉希雅'3.m4a", 1),
]
NEW_NEG = [
    ("近音 爱你老师", "'爱你老师'.m4a"),
    ("近音 雅诗兰黛", "'雅诗兰黛'.m4a"),
    ("近音 米雅", "'米雅'.m4a"),
    ("竞品唤醒 天猫精灵", "'天猫精灵'.m4a"),
    ("应答语 我没听清", "'我没听清,请再说一遍'.m4a"),
]
NEW_NOISE = [
    ("机械键盘噪音", "机械键盘噪音.m4a", 0),
    ("环境音（安静房间）", "环境音.m4a", 1),
]
# 基线对照（上一批真人件，同一管线口径）
BASE = [
    ("13次呼唤整段(基线)", "13次爱莉希雅呼唤.m4a", 13),
    ("基线近音 爱莉雅", "'爱莉雅'.m4a", 0),
    ("基线近音 米雅希", "'米雅希'.m4a", 0),
    ("基线近音 希雅老师", "'希雅老师'.m4a", 0),
]


def decode(path):
    import av
    res = av.AudioResampler(format="s16", layout="mono", rate=SR)
    out = []
    with av.open(path) as c:
        st = c.streams.audio[0]
        for f in c.decode(st):
            for r in res.resample(f):
                out.append(r.to_ndarray().reshape(-1))
    return np.concatenate(out).astype(np.int16)


def load_wav(p):
    import wave
    with wave.open(p, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def get_model(name, onnx):
    import openwakeword
    m = openwakeword.Model(wakeword_models=[onnx], inference_framework="onnx")
    m.reset()
    return m


def scores(name, audio, onnx):
    m = get_model(name, onnx)
    return [float(m.predict(audio[i:i + CHUNK]).get(name, 0.0))
            for i in range(0, max(1, len(audio) - CHUNK), CHUNK)]


def events_impl(name, audio, onnx):
    m = get_model(name, onnx)
    ev = []
    for i in range(0, max(1, len(audio) - CHUNK), CHUNK):
        s = float(m.predict(audio[i:i + CHUNK]).get(name, 0.0))
        if s >= THR:
            t = i / SR
            if ev and (t - ev[-1][0]) < GAP:
                continue
            ev.append((t, s))
            m.reset()
    return ev


def peak_n(name, audio, onnx, n=NINST):
    return [round(max(scores(name, audio, onnx)), 3) for _ in range(n)]


def rms(a):
    return float(np.sqrt(np.mean(np.square(a.astype(np.float64) / 32768.0))))


def main() -> int:
    models = sys.argv[1:] or ["aili_xiya_v0.9", "aili_xiya_v0.6"]
    items = [(k, os.path.join(REC, f), exp, "pos") for k, f, exp in NEW_POS] + \
           [(k, os.path.join(REC, f), 0, "neg") for k, f in NEW_NEG] + \
           [(k, os.path.join(REC, f), exp, "noise") for k, f, exp in NEW_NOISE] + \
           [(k, os.path.join(REC, f), exp, "base") for k, f, exp in BASE]

    print(f"逐件解码（阈值 {THR}，冷却 {GAP} s，复测 {NINST} 实例）", flush=True)
    audios = {}
    for k, p, exp, kind in items:
        a = decode(p)
        audios[k] = a
        print(f"  {k} [{kind}] {len(a)/SR:.2f} s rms={rms(a):.4f} 期望检出 {exp}", flush=True)

    # 全矩阵补充集（与既往 3 轮同一口径）：合成对抗 / 定标纯噪声 / 长噪音低分窗
    base3 = os.path.join(OUT, "aili_xiya_v0.3", "negative_test")
    adv_files = sorted(os.listdir(base3))[::8][:20]
    adv = np.concatenate([load_wav(os.path.join(base3, f)) for f in adv_files])
    V6 = os.path.join(OUT, "aili_xiya_v0.6")
    pure = np.concatenate([load_wav(os.path.join(V6, "negative_train", f"noise_tr_{i}.wav")) for i in range(1210, 1214)]
                          + [load_wav(os.path.join(V6, "negative_test", f"noise_te_{i}.wav")) for i in range(1210, 1214)])
    V9 = os.path.join(OUT, "aili_xiya_v0.9")
    longn = np.concatenate([load_wav(os.path.join(V9, "negative_train", f"noise_tr_{i}.wav")) for i in (1300, 1301, 1302)]
                           + [load_wav(os.path.join(V9, "negative_test", "noise_te_1300.wav"))])
    extra = [("合成对抗 20 条", adv, 4), ("定标纯噪声 16 s", pure, 0), ("长噪音 4 段", longn, 0)]

    for name in models:
        onnx = os.path.join(OUT, name, f"{name}.onnx")
        if not os.path.exists(onnx):
            print(f"\n[{name}] 模型不存在，跳过", flush=True)
            continue
        print(f"\n[{name}] 部署管线（1280 chunk、检出后 reset、冷却 {GAP}s）", flush=True)
        fpn = fpp = 0
        for k, p, exp, kind in items:
            a = audios[k]
            ev = events_impl(name, a, onnx)
            mx = max((s for _, s in ev), default=0.0)
            ok = "OK" if len(ev) >= exp and kind == "pos" else ("OK" if len(ev) <= exp and kind != "pos" else "BAD")
            if kind == "neg":
                fpn += len(ev)
            if kind == "pos":
                fpp += len(ev)
            print(f"  {k}：检出 {len(ev)} 次（期望 {exp}）max={mx:.3f} -> {ok}", flush=True)
        print(f"  汇总：新正样本检出合计 {fpp}，新负样本（近音/竞品/应答语）fp = {fpn}", flush=True)
        for k, a, exp in extra:
            ev = events_impl(name, a, onnx)
            print(f"  {k}：检出 {len(ev)}（期望 {exp}）", flush=True)
        print(f"  HB-032 复测（{NINST} 次独立实例峰值）：", flush=True)
        for k, p, exp, kind in items:
            if kind in ("neg", "noise", "base"):
                print(f"    {k}: {peak_n(name, audios[k], onnx)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
