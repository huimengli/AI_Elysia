# -*- coding: utf-8 -*-
"""Probe /tts 400 response body."""
import json
import urllib.error
import urllib.parse
import urllib.request

params = {
    "text": "你好，我是贾维斯。",
    "text_lang": "zh",
    "ref_audio_path": r"F:\BaiduNetdiskDownload\爱莉希雅\【GPT-SoVITS 2.0】爱莉希雅\参考音频\【感动】欸嘿，大家笑一笑，好吗？.wav",
    "prompt_lang": "zh",
    "prompt_text": "欸嘿，大家笑一笑，好吗？",
    "speed_factor": 1.0,
    "text_split_method": "cut5",
}
url = "http://127.0.0.1:9880/tts?" + urllib.parse.urlencode(params)
try:
    with urllib.request.urlopen(url, timeout=180) as r:
        print("HTTP", r.status, "bytes:", len(r.read()), flush=True)
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "replace")
    print("HTTP", e.code, flush=True)
    print("BODY:", body[:1000], flush=True)
