# -*- coding: utf-8 -*-
"""Check torchcodec wheels on tuna mirror."""
import re
import urllib.request

URL = "https://pypi.tuna.tsinghua.edu.cn/simple/torchcodec/"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
files = re.findall(r'href="([^"]+)"', html)
wheels = [f for f in files if f.endswith(".whl")]
print("total files:", len(files), flush=True)
for w in wheels:
    print("WHL:", w, flush=True)
win = [w for w in wheels if "win" in w]
print("WIN wheels:", win, flush=True)
