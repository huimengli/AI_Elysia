"""Batch download + install: matplotlib and its dep chain."""
import os
import subprocess
import sys

sys.path.insert(0, ".")
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
from _dl_wheels import pick_wheel  # noqa: E402

NAMES = [
    "matplotlib", "contourpy", "cycler", "fonttools", "kiwisolver",
    "packaging", "pyparsing", "python-dateutil", "six", "pillow",
]
os.makedirs("_wheels", exist_ok=True)
files = []
for n in NAMES:
    u = pick_wheel(n)
    fn = f"_wheels/{u.rsplit('/', 1)[-1]}"
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        print(f"SKIP {fn}", flush=True)
    else:
        import urllib.request
        print(f"GET {u}", flush=True)
        with urllib.request.urlopen(u, timeout=60) as r, open(fn, "wb") as f:
            f.write(r.read())
        print(f"  -> {fn} ({os.path.getsize(fn)} bytes)", flush=True)
    files.append(fn)
cmd = [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", *files]
print("RUN", " ".join(cmd), flush=True)
rc = subprocess.call(cmd)
print(f"pip rc={rc}", flush=True)
raise SystemExit(rc)
