# -*- coding: utf-8 -*-
"""List GPT-SoVITS tags via GitHub API through ghproxy."""
import json
import urllib.request

for url in (
    "https://ghproxy.net/https://api.github.com/repos/RVC-Boss/GPT-SoVITS/tags?per_page=50",
    "https://api.github.com/repos/RVC-Boss/GPT-SoVITS/tags?per_page=50",
):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
        print("OK via", url.split("/")[2], flush=True)
        for t in data:
            print(" tag:", t["name"], flush=True)
        break
    except Exception as e:
        print("fail", url, "->", e, flush=True)
