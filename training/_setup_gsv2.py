"""Temporary: finish .venv-gsv for GPT-SoVITS api_v2 (batched installs + portable ffmpeg). Delete after use."""
import os
import subprocess
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(ROOT, ".venv-gsv")
PIP = os.path.join(VENV, "Scripts", "pip.exe")
PY = os.path.join(VENV, "Scripts", "python.exe")
TUNA = "https://pypi.tuna.tsinghua.edu.cn/simple"
RUNTIME = os.path.join(ROOT, "GPT-SoVITS-main", "runtime")

FFMPEG_ZIP = os.path.join(ROOT, "_ffmpeg.zip")
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def run(cmd, timeout):
    print(f"$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {cmd}")
    return r


# 1) portable ffmpeg (api_v2 hardcodes GPT-SoVITS-main/runtime/ffmpeg.exe)
ffmpeg_exe = os.path.join(RUNTIME, "ffmpeg.exe")
if not os.path.exists(ffmpeg_exe):
    print("Downloading static ffmpeg build ...", flush=True)
    ctx = __import__("ssl")._create_unverified_context()
    with urllib.request.urlopen(FFMPEG_URL, context=ctx) as resp, open(FFMPEG_ZIP, "wb") as f:
        __import__("shutil").copyfileobj(resp, f)
    size = os.path.getsize(FFMPEG_ZIP)
    print(f"ffmpeg zip downloaded: {size} bytes", flush=True)
    if size < 30_000_000:
        raise RuntimeError(f"suspiciously small ffmpeg zip: {size}")
    os.makedirs(RUNTIME, exist_ok=True)
    with zipfile.ZipFile(FFMPEG_ZIP) as z:
        for name in z.namelist():
            base = os.path.basename(name)
            if base in ("ffmpeg.exe", "ffprobe.exe"):
                with z.open(name) as src, open(os.path.join(RUNTIME, base), "wb") as dst:
                    dst.write(src.read())
    os.remove(FFMPEG_ZIP)
    print("ffmpeg.exe + ffprobe.exe placed in runtime/", flush=True)
else:
    print("ffmpeg.exe already present", flush=True)

BASE = [PIP, "install", "-i", TUNA, "--no-cache-dir", "--timeout", "60", "--retries", "5"]

# 2A) small / fast wheels
run(BASE + ["numpy<2.0", "scipy", "librosa==0.10.2", "numba", "tqdm", "cn2an",
            "pypinyin", "g2p_en", "chardet", "PyYAML", "psutil", "jieba", "jieba_fast",
            "wordsegment", "rotary_embedding_torch", "ToJyutping", "ko_pron", "g2pk2",
            "split-lang", "fast_langdetect>=0.3.1", "sentencepiece", "av",
            "ffmpeg-python"], 1800)
print("BATCH_A_DONE", flush=True)

# 2B) medium wheels
run(BASE + ["peft<0.18.0", "transformers>=4.51,<5", "pydantic<=2.10.6",
            "torchmetrics<=1.5", "x_transformers", "fastapi[standard]>=0.115.2"], 2400)
print("BATCH_B_DONE", flush=True)

# 2C) heavy wheels (onnxruntime-gpu ~130MB+, opencc may build from sdist)
run(BASE + ["onnxruntime-gpu", "opencc"], 2400)
print("BATCH_C_DONE", flush=True)

# 3) import smoke test
r = subprocess.run([PY, "-c",
                    "import torch, torchaudio, librosa, numpy, peft, transformers, "
                    "fastapi, uvicorn, onnxruntime; print('GSV_IMPORTS_OK', "
                    "torch.__version__, numpy.__version__)"],
                   cwd=ROOT, timeout=300)
if r.returncode != 0:
    raise RuntimeError("import smoke test failed")
print("SETUP_GSV2_DONE", flush=True)
