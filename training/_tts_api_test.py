"""Temporary: smoke test GPT-SoVITS api_v2 /tts endpoint. Delete after use."""
import io
import json
import os
import time
import urllib.parse
import urllib.request
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "http://127.0.0.1:9880/tts"
REF = os.path.join(ROOT, "GPT-SoVITS-main", "ref_audio", "Elysia_ref_gandong.wav")

params = {
    "text": "欸嘿，大家笑一笑，好吗？我是 Jarvis，你的 AI 助手。",
    "text_lang": "zh",
    "ref_audio_path": REF,
    "prompt_lang": "zh",
    "prompt_text": "欸嘿，大家笑一笑，好吗？",
    "speed_factor": 1.0,
    "text_split_method": "cut5",
}
url = API + "?" + urllib.parse.urlencode(params)
t0 = time.time()
with urllib.request.urlopen(url, timeout=600) as r:
    data = r.read()
elapsed = time.time() - t0

out_path = os.path.join(ROOT, "_tts_out.wav")
with open(out_path, "wb") as f:
    f.write(data)

ok = True
details = []
if len(data) < 100_000:
    ok = False
    details.append(f"wav too small: {len(data)} bytes")
try:
    with wave.open(io.BytesIO(data)) as w:
        rate = w.getframerate()
        nframes = w.getnframes()
        ch = w.getnchannels()
        dur = nframes / rate if rate else 0
    details.append(f"rate={rate} ch={ch} dur={dur:.1f}s")
    if dur < 1.0:
        ok = False
        details.append("duration < 1s")
except Exception as e:
    ok = False
    details.append(f"wav parse failed: {e}")

print(f"TTS_API elapsed={elapsed:.1f}s size={len(data)}", flush=True)
print("TTS_API_RESULT: " + ("PASS" if ok else "FAIL") + f" {'; '.join(details)}", flush=True)
