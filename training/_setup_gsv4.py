# -*- coding: utf-8 -*-
"""GPT-SoVITS venv deps, batch 4.

Lessons from pwsh-77 / pwsh-89:
- jieba has NO wheel (sdist zip only) -> PEP517 build isolation creates a temp
  venv under %LOCALAPPDATA%\\Temp (outside sandbox workspace) -> deterministic
  hang at "Installing build dependencies: started".
  Fix: preinstall setuptools+wheel into .venv-gsv, then --no-build-isolation
  (build uses the venv's own setuptools; no temp env, no build-dep fetch).
- jieba_fast: sdist only + C extension (needs cython/compiler) -> skipped
  (optional dep; GPT-SoVITS falls back to plain jieba).
- Everything else in these batches is wheel-only.
"""
import subprocess
import sys

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
PIP = [r"C:\Users\楼听\Desktop\git\JarvisAi\.venv-gsv\Scripts\pip.exe",
       "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
       "--no-cache-dir", "--timeout", "60", "--retries", "3"]
PY = r"C:\Users\楼听\Desktop\git\JarvisAi\.venv-gsv\Scripts\python.exe"
TIMEOUT = 900


def run(args, tag, extra=None):
    cmd = PIP + (extra or []) + args
    print(f"\n$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, timeout=TIMEOUT)
    if r.returncode != 0:
        print(f"BATCH_{tag}_FAILED rc={r.returncode}", flush=True)
        sys.exit(1)
    print(f"BATCH_{tag}_DONE", flush=True)


def main():
    run(["setuptools", "wheel"], "S0")
    run(["cn2an", "pypinyin", "g2p_en", "chardet", "PyYAML", "psutil",
         "wordsegment"], "A2A")
    run(["jieba"], "A2B", extra=["--no-build-isolation"])
    run(["rotary_embedding_torch", "ToJyutping", "ko_pron", "g2pk2",
         "split-lang", "fast_langdetect>=0.3.1", "sentencepiece"], "A3")
    run(["av", "ffmpeg-python"], "A4")
    run(["peft<0.18.0", "transformers>=4.51,<5", "pydantic<=2.10.6",
         "torchmetrics<=1.5", "x_transformers",
         "fastapi[standard]>=0.115.2"], "B")
    try:
        run(["onnxruntime-gpu", "opencc"], "C")
    except SystemExit:
        # opencc (C ext) may lack a wheel; pure-python fallback package name
        run(["onnxruntime-gpu"], "C1")
        run(["opencc-python-reimplemented"], "C2")

    # Import smoke (module-level only; full TTS import tested at api_v2 boot)
    smoke = (
        "import torch, numpy, scipy, librosa, numba, tqdm, peft, transformers, "
        "fastapi, pydantic, onnxruntime, opencc, cn2an, pypinyin, jieba, "
        "wordsegment, sentencepiece, av, g2p_en; "
        "print('GSV_IMPORTS_OK', torch.__version__)"
    )
    r = subprocess.run([PY, "-u", "-c", smoke], cwd=ROOT, timeout=600)
    if r.returncode != 0:
        print("SMOKE_FAILED", flush=True)
        sys.exit(1)
    print("ALL_BATCHES_DONE", flush=True)


if __name__ == "__main__":
    main()
