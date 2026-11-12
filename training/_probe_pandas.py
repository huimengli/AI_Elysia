"""List pandas win_amd64 wheels on the mirror."""
import re
import urllib.request

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple/"
with urllib.request.urlopen(MIRROR + "pandas/", timeout=30) as r:
    html = r.read().decode("utf-8", errors="replace")
hs = [h.split("#")[0] for h in re.findall(r'href="([^"]+\.(?:whl|tar\.gz))', html)]
win = sorted(h for h in hs if "win_amd64" in h and "-cp312-" in h)
print("total files:", len(hs), "| cp312 win_amd64:", len(win))
for h in win:
    print(" ", h)
