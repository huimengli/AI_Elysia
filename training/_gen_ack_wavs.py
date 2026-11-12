"""Generate pre-synthesized wake-ack wavs from tts.ack_phrases via GPT-SoVITS.

Run once (and again whenever the voice/reference audio changes):
    python _gen_ack_wavs.py

Output: jarvis/data/ack/ack_01.wav ... ack_NN.wav (24 kHz int16, same as tts.py playback).
Requires GPT-SoVITS api_v2 running on :9880.
"""
from __future__ import annotations

import io
import sys
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
tts_cfg = cfg.get("tts", {})
gsv = tts_cfg.get("gptsovits", {})
api_url = gsv.get("api_url", "http://127.0.0.1:9880/tts")
phrases = tts_cfg.get("ack_phrases") or []
if not phrases:
    sys.exit("tts.ack_phrases is empty in config.yaml")

out_dir = ROOT / str(tts_cfg.get("ack_dir", "jarvis/data/ack"))
out_dir.mkdir(parents=True, exist_ok=True)

ok = 0
for i, text in enumerate(phrases, start=1):
    out = out_dir / f"ack_{i:02d}.wav"
    params = {
        "text": text,
        "text_lang": gsv.get("text_lang", "zh"),
        "ref_audio_path": gsv.get("ref_audio_path", ""),
        "prompt_lang": gsv.get("prompt_lang", "zh"),
        "prompt_text": gsv.get("prompt_text", ""),
        "speed_factor": 1.0,
        "text_split_method": "cut5",
    }
    url = f"{api_url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=180) as r:
            wav_bytes = r.read()
        with wave.open(io.BytesIO(wav_bytes), "rb") as w:
            secs = w.getnframes() / max(w.getframerate(), 1)
        out.write_bytes(wav_bytes)
        ok += 1
        print(f"[gen_ack] {out.name}: {len(wav_bytes)} bytes, ~{secs:.2f}s <- {text}")
    except Exception as e:
        print(f"[gen_ack] FAIL {text!r}: {e}")

print(f"[gen_ack] done: {ok}/{len(phrases)} written to {out_dir}")
sys.exit(0 if ok == len(phrases) else 1)
