r"""Acceptance check for the self-trained 爱莉希雅 wake word ONNX.

Loads openWakeWord/output/aili_xiya_v0.1/aili_xiya_v0.1.onnx and measures,
over a sample of generated val/test clips:
  * positive recall  — fraction of 爱莉希雅 clips whose max frame score >= t
  * negative false   — fraction of adversarial clips whose max frame score >= t
for several candidate thresholds. Writes a summary to _t2_verify_result.txt.

Run:  .venv\Scripts\python.exe _t2_verify_onnx.py [n_clips_per_set] [model_name]
Exit code: 0 if recall>=0.9 and false<=0.1 at the best threshold, else 1.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
MODEL_NAME = sys.argv[2] if len(sys.argv) > 2 else "aili_xiya_v0.1"
OUT = ROOT / "openWakeWord" / "output" / MODEL_NAME
ONNX = OUT / f"{MODEL_NAME}.onnx"
POS_DIR = OUT / "positive_test"
NEG_DIR = OUT / "negative_test"

n_each = int(sys.argv[1]) if len(sys.argv) > 1 else 25
THRESHOLDS = [0.4, 0.5, 0.6, 0.7, 0.8]


def max_score(model, wav: Path) -> float:
    preds = model.predict_clip(str(wav), padding=1, chunk_size=1280)
    scores = []
    for p in preds:
        v = p.get(MODEL_NAME)
        if v is None:
            v = next(iter(p.values()))
        scores.append(float(v))
    return max(scores) if scores else 0.0


def main() -> int:
    if not ONNX.exists():
        print(f"FAIL: {ONNX} does not exist yet (training not finished?)")
        return 2

    import openwakeword
    model = openwakeword.Model(wakeword_models=[str(ONNX)])
    print(f"loaded: {ONNX}")

    pos_wavs = sorted(POS_DIR.glob("*.wav"))[:n_each]
    neg_wavs = sorted(NEG_DIR.glob("*.wav"))[:n_each]
    if not pos_wavs or not neg_wavs:
        print(f"FAIL: need clips in {POS_DIR} and {NEG_DIR} (got {len(pos_wavs)}/{len(neg_wavs)})")
        return 2

    lines = [f"n_per_set={n_each}", f"model={ONNX.name}"]
    pos_scores, neg_scores = [], []
    for i, w in enumerate(pos_wavs):
        s = max_score(model, w)
        pos_scores.append(s)
        print(f"[pos {i + 1}/{len(pos_wavs)}] {w.name} max={s:.3f}")
    for i, w in enumerate(neg_wavs):
        s = max_score(model, w)
        neg_scores.append(s)
        print(f"[neg {i + 1}/{len(neg_wavs)}] {w.name} max={s:.3f}")

    lines += [
        f"pos mean/max = {np.mean(pos_scores):.3f}/{np.max(pos_scores):.3f}",
        f"neg mean/max = {np.mean(neg_scores):.3f}/{np.max(neg_scores):.3f}",
        "",
        "threshold | pos_recall | neg_false",
    ]
    best = None
    for t in THRESHOLDS:
        recall = float(np.mean([s >= t for s in pos_scores]))
        false = float(np.mean([s >= t for s in neg_scores]))
        lines.append(f"   {t:.1f}   |    {recall:.2f}   |   {false:.2f}")
        if recall >= 0.9 and false <= 0.1:
            best = t

    ok = best is not None
    lines += ["", f"VERDICT: {'PASS' if ok else 'FAIL'} (best threshold {best})"]
    text = "\n".join(lines)
    out_file = ROOT / "_t2_verify_result.txt"
    out_file.write_text(text, encoding="utf-8")
    print(text)
    print(f"\n-> {out_file}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
