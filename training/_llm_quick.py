"""Minimal non-streaming probe of llama.cpp chat endpoint."""
import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL = "F:/魔搭社区/Qwen3.8-27B-Q4_K_M-GGUF/Swift-1.5-Qwen3.8-27B-GSQ-RCO-IQ2_XS-mtp.gguf"
body = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are 爱莉希雅."},
        {"role": "user", "content": "你好"},
    ],
    "temperature": 0.7,
    "max_tokens": 64,
    "stream": False,
}
t0 = time.time()
try:
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    dt = time.time() - t0
    text = data["choices"][0]["message"]["content"]
    print(f"OK total={dt:.1f}s response={text!r}", flush=True)
except Exception as e:
    print(f"FAIL after {time.time()-t0:.1f}s: {type(e).__name__}: {e}", flush=True)
