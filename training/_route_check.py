"""Fresh-process check: config routing + direct openai-path call timing."""
import json
import sys
import time

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
llm = cfg["llm"]
active = llm.get("active_provider", "ollama")
provider = llm.get("providers", {}).get(active, {})
ptype = provider.get("type", "ollama")
print(f"routing: active={active} ptype={ptype}", flush=True)

if ptype == "openai":
    import httpx

    client_h = httpx.Client(base_url=provider["base_url"], timeout=180.0)
    body = {
        "model": provider["model"],
        "messages": [
            {"role": "system", "content": "You are 爱莉希雅 (Elysia). Always reply in Simplified Chinese."},
            {"role": "user", "content": "你叫什么名字？"},
        ],
        "temperature": 0.7,
        "max_tokens": 256,
        "stream": True,
        "extra_body": None,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    body.pop("extra_body")
    t0 = time.time()
    ttft = None
    text = ""
    with client_h.stream("POST", "/chat/completions", json=body) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            chunk = json.loads(payload)
            choices = chunk.get("choices") or []
            if not choices:
                continue
            c = choices[0].get("delta", {}).get("content")
            if c:
                if ttft is None:
                    ttft = time.time() - t0
                text += c
    print(f"openai-path OK ttft={ttft:.1f}s total={time.time()-t0:.1f}s response={text!r}", flush=True)
