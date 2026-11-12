# -*- coding: utf-8 -*-
"""Probe full GPT-SoVITS import chain (new layout, mirrors api_v2 sys.path)."""
import os
import sys

now = r"C:\Users\楼听\Desktop\git\JarvisAi\GPT-SoVITS-main"
sys.path.append(now)
sys.path.append(os.path.join(now, "GPT_SoVITS"))

for mod in ("torchaudio", "resampy", "soundfile"):
    __import__(mod)
print("base deps OK", flush=True)

from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config  # noqa: E402
print("GSV_FULL_IMPORT_OK", flush=True)
