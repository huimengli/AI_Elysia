r"""Dry run of the augment + feature-extraction chain (T2 pre-flight).

Replicates the exact call pattern of _t2_train_cn.py's --augment_clips branch,
but on a 6-clip subset with output under _wheels/t2_dryrun/ — NEVER writing to
the real feature_save_dir (a stray .npy there would make the real augment skip).

Validates: augment_clips generator (RIR + background mixing), AudioFeatures
(onnxruntime mel + embedding), memmap .npy output shape.

Run:  .venv\Scripts\python.exe _t2_augment_dryrun.py
"""
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np  # noqa: E402
import scipy.io  # noqa: E402
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "openWakeWord" / "train_config.yaml"
DRY_DIR = ROOT / "_wheels" / "t2_dryrun"


def derive_total_length(wavs) -> int:
    """Replicates _t2_train_cn.py lines 806-817 (median + 12000, min 32000, snap-to-32000)."""
    n = min(50, len(wavs))
    durations = []
    for i in range(n):
        _, dat = scipy.io.wavfile.read(str(np.random.choice(list(wavs))))
        durations.append(len(dat))
    tl = int(round(np.median(durations) / 1000) * 1000) + 12000
    if tl < 32000:
        tl = 32000
    elif abs(tl - 32000) <= 4000:
        tl = 32000
    return tl


def main() -> int:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    model_name = config["model_name"]
    out_root = Path(config["output_dir"]) / model_name
    pos_dir = out_root / "positive_train"
    all_wavs = sorted(pos_dir.glob("*.wav"))
    clips = all_wavs[:6]
    if len(clips) < 6:
        print(f"FAIL: need >=6 clips in {pos_dir}, got {len(clips)}")
        return 2

    DRY_DIR.mkdir(parents=True, exist_ok=True)
    out_file = DRY_DIR / "positive_features_train.npy"
    if out_file.exists():
        out_file.unlink()

    total_length = derive_total_length(all_wavs)
    batch_size = config["augmentation_batch_size"]
    # Replicate trainer lines 754-759: config dirs -> individual file paths.
    rir_paths = [i.path for j in config.get("rir_paths", []) for i in os.scandir(j)]
    background_paths = []
    dup_rate = config.get("background_paths_duplication_rate", [])
    if len(dup_rate) != len(config.get("background_paths", [])):
        dup_rate = [1] * len(config.get("background_paths", []))
    for bg_dir, rate in zip(config.get("background_paths", []), dup_rate):
        background_paths.extend([i.path for i in os.scandir(bg_dir)] * rate)
    print(f"clips={len(clips)} total_length={total_length} batch_size={batch_size}")
    print(f"background_dirs={len(background_paths)} rir_dirs={len(rir_paths)}")

    # Import the real trainer module FIRST: its module-level shims (torchaudio,
    # serial ThreadPool, patched compute_features_from_generator) must be what
    # makes augment_clips work. Pull the patched names from it, not directly
    # from openwakeword (which would bind the unpatched originals).
    import _t2_train_cn
    augment_clips = _t2_train_cn.augment_clips
    compute_features_from_generator = _t2_train_cn.compute_features_from_generator

    gen = augment_clips([str(c) for c in clips],
                        total_length=total_length,
                        batch_size=batch_size,
                        background_clip_paths=background_paths,
                        RIR_paths=rir_paths)
    compute_features_from_generator(gen, n_total=len(clips),
                                    clip_duration=total_length,
                                    output_file=str(out_file),
                                    device="cpu", ncpu=2)

    arr = np.load(str(out_file), mmap_mode="r")
    print(f"npy shape={arr.shape} dtype={arr.dtype}")
    # expected: (6, frames, 96); frames derived from total_length
    ok = arr.ndim == 3 and arr.shape[0] == len(clips) and arr.shape[2] == 96
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}")
    print(f"-> {out_file}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
