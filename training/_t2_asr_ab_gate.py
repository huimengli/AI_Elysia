r"""ASR 三配置对照：whisper 现役 / sherpa 无能量门 / sherpa 能量门（records/2026-11-12-22-51-09.md）。

- 已知文本集（文件名即真值，6 件 m4a）：sim ≥0.8 计数为判据；
- 真实麦克风抓取集 `.tmp/capture_*.wav`（`jarvis/stt.py` 每次录音落盘的原始 16 k PCM，
  records/2026-11-10-17-43-08.md 的「A/B 唯一依据」），取时长 ≥3 s 的前 12 条，逐条打印两引擎文本；
- `GATE=0` 关能量门、`GATE=1` 开（默认开）。`NINST` 无意义，逐条一次。

Run:  .venv\Scripts\python.exe training\_t2_asr_ab_gate.py
"""
import os
import sys
import time
import wave

import numpy as np

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import difflib

import av
from jarvis import stt as S

SR = 16000
ATT = r"C:\Users\楼听\.dsh\attachments\v1\files"
GATE = os.environ.get("GATE", "1") == "1"
THR = float(os.environ.get("THR", "0.015"))
MODE = os.environ.get("MODE", "span")   # span = 只掐头尾静音；concat = 逐窗拼接

KNOWN = [
    ("爱莉希雅，帮我打开电视机", os.path.join(ATT, "51", "516e9597cdd7380538c1171fd314f67dc5cd6a671d0c27624c001abe0250e2c0", "'爱莉希雅, 帮我打开电视机'.m4a")),
    ("爱莉希雅，帮我打开浏览器", os.path.join(ATT, "70", "702e859a60ad2f9b5457ef545c07b7df4dcdaea793ff1d76638c4bc71a81412a", "'爱莉希雅, 帮我打开浏览器'.m4a")),
    ("你好啊爱莉希雅，你在干什么呢", os.path.join(ATT, "dd", "dd1734ff6291084fa0888071430dc4695c533bc6297763c2207bcfa3fa0d37db", "'你好啊爱莉希雅, 你在干什么呢'.m4a")),
    ("爱丽安娜", os.path.join(ATT, "64", "64087065e0813bd6f548d0cfb0b7f3807fc238d753704025f1674034d6a0a60d", "'爱丽安娜'.m4a")),
    ("爱丽丝", os.path.join(ATT, "a1", "a124044230359057f882d8b63859aba288fccf4c118b59a485e5364ce95d44e1", "'爱丽丝'.m4a")),
    ("米希雅", os.path.join(ATT, "db", "dbb1ba6881c9a1e40ab532693f507e61ddf131a234172863c133355d7d115e2a", "'米希雅'.m4a")),
]


def decode(path):
    res = av.AudioResampler(format="s16", layout="mono", rate=SR)
    out = []
    with av.open(path) as c:
        for f in c.decode(c.streams.audio[0]):
            for r in res.resample(f):
                out.append(r.to_ndarray().reshape(-1))
    a = np.concatenate(out).astype(np.int16)
    return a.astype(np.float32) / 32768.0


def load(p):
    with wave.open(p, "rb") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return a.astype(np.float32) / 32768.0


def sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def main() -> int:
    cfg = S._load_config()["stt"]
    lang = cfg.get("language", "zh")
    prompt = cfg.get("initial_prompt") or None
    wm = S._get_model()

    def whisper(a):
        t0 = time.perf_counter()
        segs, _ = wm.transcribe(a, beam_size=int(cfg.get("beam_size", 10)),
                                best_of=int(cfg.get("best_of", 5)), vad_filter=True,
                                condition_on_previous_text=False,
                                initial_prompt=prompt, language=lang)
        return " ".join(s.text.strip() for s in segs).strip(), 1000 * (time.perf_counter() - t0)

    def sherpa(a, gate: bool):
        t0 = time.perf_counter()
        body = a
        if gate:
            body = S._energy_gate(a, threshold=THR, mode=MODE)
        rec = S._get_sherpa()
        st = rec.create_stream()
        st.accept_waveform(16000, np.asarray(body, dtype=np.float32))
        rec.decode_stream(st)
        return st.result.text, 1000 * (time.perf_counter() - t0)

    sets = []
    for name, p in KNOWN:
        sets.append((f"已知:{name}", decode(p), name))
    caps = sorted([f for f in os.listdir(os.path.join(ROOT, ".tmp"))
                   if f.startswith("capture_") and f.endswith(".wav")])
    big = [f for f in caps if os.path.getsize(os.path.join(ROOT, ".tmp", f)) >= 300044][:12]
    for f in big:
        sets.append((f, load(os.path.join(ROOT, ".tmp", f)), None))

    w_ok = s0_ok = s1_ok = 0
    w_garble = s0_garble = s1_garble = 0
    w_ms = s0_ms = s1_ms = 0.0
    for tag, audio, truth in sets:
        wt, wms = whisper(audio)
        s0t, s0m = sherpa(audio, False)
        s1t, s1m = sherpa(audio, True)
        w_ms += wms
        s0_ms += s0m
        s1_ms += s1m
        if truth:
            sw, s0, s1 = sim(wt, truth), sim(s0t, truth), sim(s1t, truth)
            print(f"[{tag}] 真值={truth}", flush=True)
            print(f"  whisper  {wms:6.0f} ms: {wt}  (sim={sw:.2f})", flush=True)
            print(f"  sherpa-门 {s0m:6.0f} ms: {s0t}  (sim={s0:.2f})", flush=True)
            print(f"  sherpa+门 {s1m:6.0f} ms: {s1t}  (sim={s1:.2f})", flush=True)
            w_ok += 1 if sw >= 0.8 else 0
            s0_ok += 1 if s0 >= 0.8 else 0
            s1_ok += 1 if s1 >= 0.8 else 0
            w_garble += 1 if sw < 0.4 else 0
            s0_garble += 1 if s0 < 0.4 else 0
            s1_garble += 1 if s1 < 0.4 else 0
        else:
            print(f"[{tag}] {len(audio)/SR:.2f} s", flush=True)
            print(f"  whisper  {wms:6.0f} ms: {wt}", flush=True)
            print(f"  sherpa-门 {s0m:6.0f} ms: {s0t}", flush=True)
            print(f"  sherpa+门 {s1m:6.0f} ms: {s1t}", flush=True)
            w_garble += 1 if wt == "" else 0
            s0_garble += 1 if s0t == "" else 0
            s1_garble += 1 if s1t == "" else 0
    n = len(KNOWN)
    print(f"\n已知文本集 sim>=0.8：whisper {w_ok}/{n}，sherpa 无门 {s0_ok}/{n}，sherpa 能量门 {s1_ok}/{n}", flush=True)
    print(f"乱码/空件数（全部 {len(sets)} 件）：whisper {w_garble}，sherpa 无门 {s0_garble}，sherpa 能量门 {s1_garble}", flush=True)
    print(f"总耗时（全部 {len(sets)} 件）：whisper {w_ms:.0f} ms，sherpa 无门 {s0_ms:.0f} ms，sherpa 能量门 {s1_ms:.0f} ms", flush=True)
    print(f"[gate] MODE={MODE} THR={THR}，抓取件 {len(big)} 条", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
