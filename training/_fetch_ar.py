# -*- coding: utf-8 -*-
"""Fetch AR/ from GPT-SoVITS v2 tag (old layout) into workspace repo."""
import os
import tarfile
import urllib.request

URL = ("https://ghproxy.net/https://github.com/RVC-Boss/GPT-SoVITS/"
       "archive/refs/tags/v2.tar.gz")
DEST_DIR = r"C:\Users\楼听\Desktop\git\JarvisAi\GPT-SoVITS-main"
TAR = r"C:\Users\楼听\Desktop\git\JarvisAi\_gsv_v2.tar.gz"

print("downloading v2 tag...", flush=True)
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=180) as r, open(TAR, "wb") as f:
    while True:
        chunk = r.read(1 << 16)
        if not chunk:
            break
        f.write(chunk)
print("bytes:", os.path.getsize(TAR), flush=True)

with tarfile.open(TAR) as tf:
    names = [m.name for m in tf.getmembers()]
    tops = sorted({n.split("/")[1] for n in names if "/" in n})
    print("top-level entries:", tops, flush=True)
    prefix = None
    for t in tops:
        if t == "AR":
            prefix = None  # handled below via per-name check
    members = [m for m in tf.getmembers()
               if m.name.split("/", 1)[1].split("/")[0] == "AR"]
    print("AR members:", len(members), flush=True)
    if members:
        tf.extractall(DEST_DIR, members=members)

os.remove(TAR)
print("t2s exists:", os.path.exists(
    os.path.join(DEST_DIR, "AR", "models", "t2s_lightning_module.py")),
    flush=True)
