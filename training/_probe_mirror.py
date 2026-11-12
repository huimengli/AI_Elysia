"""Probe Tsinghua mirror simple index for a package name."""
import re
import sys
import urllib.request

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple/"
name = sys.argv[1] if len(sys.argv) > 1 else "lightning_utilities"
with urllib.request.urlopen(MIRROR + name + "/", timeout=30) as r:
    html = r.read().decode("utf-8", errors="replace")
print("html_len:", len(html))
hrefs = re.findall(r'href="([^"]+)"', html)
print("total hrefs:", len(hrefs))
wheels = [h for h in hrefs if h.endswith(".whl")]
sdists = [h for h in hrefs if h.endswith(".tar.gz")]
print("wheels:", len(wheels), "sdists:", len(sdists))
for h in (wheels[:3] + sdists[:2]):
    print(" ", h)
