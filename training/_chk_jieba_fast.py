# -*- coding: utf-8 -*-
"""Check jieba_fast wheel availability on tuna mirror."""
import re
import urllib.request

URL = "https://pypi.tuna.tsinghua.edu.cn/simple/jieba-fast/"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
files = re.findall(r'href="([^"]+)"', html)
wheels = [f for f in files if f.endswith(".whl")]
print("total files:", len(files), flush=True)
for w in wheels:
    print("WHL:", w, flush=True)
win_cp312 = [w for w in wheels
             if "cp312" in w and ("win_amd64" in w or "win32" in w)]
print("WIN cp312 wheels:", win_cp312, flush=True)
