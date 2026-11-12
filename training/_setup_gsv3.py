# -*- coding: utf-8 -*-
"""GPT-SoVITS venv setup, batch 3.

Batch A of pwsh-77 stalled in pip collection phase (nothing persisted),
so this splits the work into 6 small batches with 900s timeouts to localize
any stall. opencc falls back to opencc-python-reimplemented (pure Python).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PY = ROOT / ".venv-gsv" / "Scripts" / "python.exe"
PIP = ROOT / ".venv-gsv" / "Scripts" / "pip.exe"
MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"


def run(packages: list[str], timeout: int = 900) -> None:
    cmd = [str(PIP), "install", "-i", MIRROR, "--no-cache-dir",
           "--timeout", "60", "--retries", "3"] + packages
    print(f"$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, timeout=timeout)
    if r.returncode != 0:
        sys.exit(f"pip batch failed rc={r.returncode}: {packages}")


def try_run(packages: list[str], fallback: list[str] | None, timeout: int = 900) -> None:
    cmd = [str(PIP), "install", "-i", MIRROR, "--no-cache-dir",
           "--timeout", "60", "--retries", "3"] + packages
    print(f"$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, timeout=timeout)
    if r.returncode != 0 and fallback:
        print(f"batch failed rc={r.returncode}; fallback -> {fallback}", flush=True)
        cmd2 = [str(PIP), "install", "-i", MIRROR, "--no-cache-dir",
                "--timeout", "60", "--retries", "3"] + fallback
        r2 = subprocess.run(cmd2, cwd=ROOT, timeout=timeout)
        if r2.returncode != 0:
            sys.exit(f"pip batch+fallback failed rc={r2.returncode}: {packages}")


def main() -> None:
    # A1 core science stack (large wheels, fast on mirror)
    run(["numpy<2.0", "scipy", "librosa==0.10.2", "numba", "tqdm"])
    print("BATCH_A1_DONE", flush=True)

    # A2 CJK text tools (light)
    run(["cn2an", "pypinyin", "g2p_en", "chardet", "PyYAML", "psutil",
         "jieba", "jieba_fast", "wordsegment"])
    print("BATCH_A2_DONE", flush=True)

    # A3 misc phonetics + tokenizer (light)
    run(["rotary_embedding_torch", "ToJyutping", "ko_pron", "g2pk2",
         "split-lang", "fast_langdetect>=0.3.1", "sentencepiece"])
    print("BATCH_A3_DONE", flush=True)

    # A4 media (av wheel is large)
    run(["av", "ffmpeg-python"])
    print("BATCH_A4_DONE", flush=True)

    # B ML / API stack
    run(["peft<0.18.0", "transformers>=4.51,<5", "pydantic<=2.10.6",
         "torchmetrics<=1.5", "x_transformers", "fastapi[standard]>=0.115.2"])
    print("BATCH_B_DONE", flush=True)

    # C onnx + opencc (fallback to pure-python reimplementation)
    try_run(["onnxruntime-gpu"], None)
    try_run(["opencc"], ["opencc-python-reimplemented"])
    print("BATCH_C_DONE", flush=True)

    # Import smoke test
    code = (
        "import importlib\n"
        "mods = ['torch','torchaudio','librosa','numpy','scipy','numba','peft',"
        "'transformers','fastapi','uvicorn','onnxruntime','opencc','pydantic',"
        "'tqdm','psutil','yaml','chardet','pypinyin','jieba','wordsegment',"
        "'g2p_en','sentencepiece','av']\n"
        "for m in mods:\n    importlib.import_module(m)\n"
        "print('GSV_IMPORTS_OK', flush=True)"
    )
    r = subprocess.run([str(VENV_PY), "-u", "-c", code], cwd=ROOT, timeout=600)
    if r.returncode != 0:
        sys.exit(f"import smoke test failed rc={r.returncode}")


if __name__ == "__main__":
    main()
