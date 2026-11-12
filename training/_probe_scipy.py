"""List scipy cp312 win wheels on the mirror."""
import re
import urllib.request

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple/"
with urllib.request.urlopen(MIRROR + "scipy/", timeout=30) as r:
    html = r.read().decode("utf-8", errors="replace")
hrefs = [h.split("#")[0] for h in re.findall(r'href="([^"]+\.whl)"', html)]
cands = sorted(h for h in hrefs if "-cp312-cp312-win_amd64" in h)
print("cp312 win wheels:", len(cands))
for h in cands:
    m = re.search(r"scipy-(\d+\.\d+\.\d+)", h)
    print(" ", m.group(1) if m else h)
