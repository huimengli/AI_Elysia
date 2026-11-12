"""Temporary: direct test of jarvis.tts gptsovits path (no LLM, no playback). Delete after use."""
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, r"C:\Users\楼听\Desktop\git\JarvisAi\training")
os.chdir(ROOT)

import yaml

with open(os.path.join(ROOT, "config.yaml"), encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
assert cfg["tts"]["provider"] == "gptsovits", f"provider={cfg['tts']['provider']}"

from jarvis.tts import _active_provider, _synth  # noqa: E402

assert _active_provider() == "gptsovits"

text = "你好，我是 Jarvis。这是爱莉希雅的声音测试。"
t0 = time.time()
pcm, rate = _synth(text)
elapsed = time.time() - t0

ok = len(pcm) > 40_000 and rate in (24000, 32000)
dur = len(pcm) / 2 / rate if rate else 0
print(f"TTS_DIRECT elapsed={elapsed:.1f}s pcm_bytes={len(pcm)} rate={rate} dur={dur:.1f}s", flush=True)
print("TTS_DIRECT_RESULT: " + ("PASS" if ok else "FAIL"), flush=True)
