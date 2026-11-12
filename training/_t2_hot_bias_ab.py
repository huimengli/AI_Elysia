r"""热词表 + whisper initial_prompt 偏置 A/B（records/2026-11-12-23-08-34.md 第 3 轮）。

- **表行为**：写入、count 累加、`kind`、上限淘汰（造 >200 条必须回到 `_HOT_CAP` 行）；
- **A/B 偏置**：A = 只用 config 的 `stt.initial_prompt`（现状，`set_hot_words([])`），
  B = 灌入 `hot_phrases` top-N（`set_hot_words(...)`），同一批已知 6 件（文件名即真值）
  跑 whisper，比 `sim ≥0.8` 计数与逐件转写；判据 = B ≥ A 且逐件不变差。
- 已知 6 件的路径与解码直接复用 `training/_t2_asr_ab_gate.py`（同一批数据，不重复实现）。

Run:  $env:HF_ENDPOINT='https://hf-mirror.com'; $env:HF_HOME='<repo>\.hf-cache';
      $env:HF_HUB_DISABLE_XET='1'; $env:MPLCONFIGDIR='<repo>\.tmp\mpl';
      .venv\Scripts\python.exe training\_t2_hot_bias_ab.py
"""
import os
import sys
from difflib import SequenceMatcher

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "training"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HOME", os.path.join(ROOT, ".hf-cache"))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("MPLCONFIGDIR", os.path.join(ROOT, ".tmp", "mpl"))

import time  # noqa: E402

import _t2_asr_ab_gate as P  # noqa: E402  复用 KNOWN/decode/load
from jarvis.memory import Memory  # noqa: E402
from jarvis import stt as S  # noqa: E402

HOT = ["爱莉希雅", "爱丽希雅", "泰利西亚", "爱丽西雅", "艾丽安娜",
       "爱莉希雅，帮我打开浏览器", "爱莉希雅，帮我打开电视机",
       "你好啊爱莉希雅，你在干什么呢", "米希雅", "爱丽丝", "爱丽安娜", "屏幕"]


def whisper_once(audio) -> tuple[str, float]:
    t0 = time.perf_counter()
    text = S.transcribe_audio(audio)
    return text, 1000 * (time.perf_counter() - t0)


def run(res_set: list[tuple], label: str) -> list[tuple]:
    out = []
    for name, audio in res_set:
        t, ms = whisper_once(audio)
        s = SequenceMatcher(None, name, t).ratio()
        out.append((name, t, s, ms))
        print(f"  [{label}] {name} → {t!r} (sim={s:.2f}, {ms:.0f} ms)", flush=True)
    ok = sum(1 for _, _, s, _ in out if s >= 0.8)
    print(f"[{label}] sim>=0.8 = {ok}/{len(out)}，总耗时 {sum(r[3] for r in out):.0f} ms", flush=True)
    return out


HOT_BIAS = os.environ.get("HOT_BIAS", "1") == "1"
STAMP = time.strftime("%Y-%m-%d-%H-%M-%S")
TMP_DB = os.path.join(ROOT, ".tmp", f"hot_probe_memory_{STAMP}.db")


def main() -> int:
    # **临时库**，不污染现役 `jarvis/data/memory.db`（第 3 轮实测造 210 条 filler 会挤掉
    # 真实热词，所以必须隔离；现役库里的 filler 行已单独清理）。
    # 绕开 `Memory.__init__`：chromadb 在这个中文用户目录的 `.tmp` 下起不来
    # （实测 `chromadb.errors.InternalError: (code: 14) unable to open database file`），
    # 而 `record_phrase` / `top_hot_phrases` / `hot_phrase_rows` 只用 `_engine` 与 `_HOT_CAP`。
    from sqlalchemy import create_engine

    mem = Memory.__new__(Memory)
    mem._engine = create_engine(f"sqlite:///{TMP_DB}")
    mem._HOT_CAP = 200
    mem._setup_db()
    for w in HOT:
        mem.record_phrase(w, "user")
    mem.record_phrase("爱莉希雅", "near_miss")
    rows = mem.hot_phrase_rows()
    print(f"[表] 行数 {len(rows)}（上限 {mem._HOT_CAP}），top6 = {mem.top_hot_phrases(6)}", flush=True)
    print(f"[表] 爱莉希雅 行 = {[r for r in rows if r[0] == '爱莉希雅']}（kind 以最后写入为准）", flush=True)
    for i in range(210):
        mem.record_phrase(f"filler{i}", "user")
    rows2 = mem.hot_phrase_rows()
    print(f"[表] 造 210 条后行数 {len(rows2)}（应 = {mem._HOT_CAP}），top5 = {[r[0] for r in rows2[:5]]}", flush=True)

    sets = [(name, P.decode(p)) for name, p in P.KNOWN]
    S.set_hot_words([])
    resA = run(sets, "A 无偏置")
    hot = mem.top_hot_phrases(12)
    hot = [h for h in hot if not h.startswith("filler")]  # 只用真热词，排除测试 filler
    if HOT_BIAS:
        S.set_hot_words(hot)
        print(f"[偏置] 注入 {len(S.get_hot_words())} 条：{S.get_hot_words()}", flush=True)
    else:
        S.set_hot_words([])
        print("[偏置] HOT_BIAS=0（默认），top-N 不灌 initial_prompt", flush=True)
    resB = run(sets, f"B 偏置={'开' if HOT_BIAS else '关'}")
    okA = sum(1 for r in resA if r[2] >= 0.8)
    okB = sum(1 for r in resB if r[2] >= 0.8)
    worse = [(n, a[1], b[1]) for (n, a, b) in zip([r[0] for r in resA], resA, resB) if b[2] < a[2] - 0.02]
    print(f"[判据] sim>=0.8：A={okA} → B={okB}（要求 B ≥ A）；变差件数 {len(worse)}：{worse}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
