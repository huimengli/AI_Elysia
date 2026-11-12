"""Temporary: set up .venv-gsv for GPT-SoVITS (CPU torch first, Tsinghua fallback). Delete after use."""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(ROOT, ".venv-gsv")
PIP = os.path.join(VENV, "Scripts", "pip.exe")
TUNA = "https://pypi.tuna.tsinghua.edu.cn/simple"
PYTORCH_CPU = "https://download.pytorch.org/whl/cpu"


def run(cmd, timeout=None):
    print(f"$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {cmd}")
    return r


# 1) venv
if not os.path.exists(PIP):
    print("Creating venv .venv-gsv ...", flush=True)
    run([sys.executable, "-m", "venv", VENV], timeout=600)

# (pip upgrade step removed: it hung 300s on a dead connection; venv pip 23.2.1 is fine)

# 2) torch + torchaudio: try CPU-only index first (smaller), fallback to Tsinghua
try:
    run([PIP, "install", "torch", "torchaudio", "--index-url", PYTORCH_CPU, "--no-cache-dir"], timeout=1800)
    print("torch from pytorch.org cpu index OK", flush=True)
except Exception as e:
    print(f"pytorch cpu index failed ({e}); falling back to Tsinghua (full CUDA build)", flush=True)
    run([PIP, "install", "torch", "torchaudio", "-i", TUNA, "--no-cache-dir"], timeout=3600)

# 3) requirements
req = os.path.join(ROOT, "GPT-SoVITS-main", "requirements.txt")
run([PIP, "install", "-r", req, "-i", TUNA, "--no-cache-dir"], timeout=5400)

print("SETUP_GSV_VENV_DONE", flush=True)
