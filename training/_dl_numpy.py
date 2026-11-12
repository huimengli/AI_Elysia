"""Download and install numpy 2.2.x cp312 win wheel (scipy 1.14.1 compatibility)."""
import os
import re
import subprocess
import sys
import urllib.request

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple/"
with urllib.request.urlopen(MIRROR + "numpy/", timeout=30) as r:
    html = r.read().decode("utf-8", errors="replace")
hrefs = re.findall(r'href="([^"]+\.(?:whl|tar\.gz))', html)
cands = [h for h in hrefs if "-cp312-cp312-win_amd64" in h and "2.2." in h]
best = max(cands, key=lambda h: re.sub(r".*numpy-(\d+\.\d+\.\d+).*", r"\1", h.split("#")[0]))
print("PICK:", best)
fn = f"_wheels/{best.split('#')[0].rsplit('/', 1)[-1]}"
os.makedirs("_wheels", exist_ok=True)
with urllib.request.urlopen(MIRROR + "numpy/" + best.split("#")[0], timeout=60) as r, open(fn, "wb") as f:
    f.write(r.read())
print("saved", fn, os.path.getsize(fn))
rc = subprocess.call([sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", "--force-reinstall", fn])
print(f"pip rc={rc}")
raise SystemExit(rc)
