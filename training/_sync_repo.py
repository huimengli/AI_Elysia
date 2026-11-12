# -*- coding: utf-8 -*-
"""Full-sync GPT-SoVITS-main from the current-main tarball on disk,
preserving local additions (weights, ref_audio, runtime, tts_infer.yaml)."""
import os
import shutil
import tarfile

ROOT = r"C:\Users\楼听\Desktop\git\JarvisAi"
REPO = os.path.join(ROOT, "GPT-SoVITS-main")
TAR = os.path.join(ROOT, "_gsv_main.tar.gz")
STAGE = os.path.join(ROOT, "_gsv_staged")

# 1) stage full tarball
if os.path.isdir(STAGE):
    shutil.rmtree(STAGE)
os.makedirs(STAGE)
with tarfile.open(TAR) as tf:
    tf.extractall(STAGE)
top = os.path.join(STAGE, "GPT-SoVITS-main")
print("staged top-level:", sorted(os.listdir(top))[:12], "...", flush=True)

# 2) copy staged files over repo (overwrite), keep local-only dirs intact
count = 0
for dirpath, dirnames, filenames in os.walk(top):
    rel = os.path.relpath(dirpath, top)
    dest_dir = REPO if rel == "." else os.path.join(REPO, rel)
    os.makedirs(dest_dir, exist_ok=True)
    for fn in filenames:
        src = os.path.join(dirpath, fn)
        dst = os.path.join(dest_dir, fn)
        shutil.copy2(src, dst)
        count += 1
print("files copied:", count, flush=True)

# 3) verify preserved local additions
for p in (
    os.path.join(REPO, "GPT_weights_v2",
                 "【GPT2.0】Elysia-e20.ckpt"),
    os.path.join(REPO, "SoVITS_weights_v2",
                 "【GPT2.0】Elysia_e24_s13080.pth"),
    os.path.join(REPO, "ref_audio", "Elysia_ref_gandong.wav"),
    os.path.join(REPO, "runtime", "ffmpeg.exe"),
    os.path.join(REPO, "GPT_SoVITS", "configs", "tts_infer.yaml"),
    os.path.join(REPO, "AR", "models", "t2s_lightning_module.py"),
    os.path.join(REPO, "text", "__init__.py"),
):
    print("exists:", os.path.exists(p), "->", p.split("GPT-SoVITS-main/")[-1],
          flush=True)

# 4) our tts_infer.yaml must still contain Elysia paths (not overwritten)
y = open(os.path.join(REPO, "GPT_SoVITS", "configs", "tts_infer.yaml"),
         encoding="utf-8").read()
print("yaml has Elysia ckpt:", "Elysia-e20" in y, flush=True)
print("yaml has Elysia pth:", "Elysia_e24_s13080" in y, flush=True)

shutil.rmtree(STAGE)
print("SYNC_DONE", flush=True)
