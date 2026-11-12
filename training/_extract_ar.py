# -*- coding: utf-8 -*-
"""Extract AR/ only from the already-downloaded GPT-SoVITS main tarball."""
import os
import tarfile

TAR = r"C:\Users\楼听\Desktop\git\JarvisAi\_gsv_main.tar.gz"
DEST_DIR = r"C:\Users\楼听\Desktop\git\JarvisAi\GPT-SoVITS-main"
PREFIX = "GPT-SoVITS-main/AR/"

with tarfile.open(TAR) as tf:
    members = [m for m in tf.getmembers() if m.name.startswith(PREFIX)]
    print("AR members:", len(members), flush=True)
    tf.extractall(DEST_DIR, members=members)

os.remove(TAR)
print("t2s exists:", os.path.exists(
    os.path.join(DEST_DIR, "AR", "models", "t2s_lightning_module.py")),
    flush=True)
