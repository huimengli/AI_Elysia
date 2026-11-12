"""List all scipy files on the mirror + check pypi.org directly."""
import re
import urllib.request

for base in ("https://pypi.tuna.tsinghua.edu.cn/simple/", "https://pypi.org/simple/"):
    try:
        with urllib.request.urlopen(base + "scipy/", timeout=30) as r:
            html = r.read().decode("utf-8", errors="replace")
        hrefs = [h.split("#")[0] for h in re.findall(r'href="([^"]+\.whl)"', html)]
        cp312win = [h for h in hrefs if "-cp312-cp312-win_amd64" in h]
        print(f"{base}: total={len(hrefs)} cp312win={len(cp312win)}")
        for h in cp312win[:10]:
            m = re.search(r"scipy-(\d+\.\d+\.\d+)", h)
            print("  ", m.group(1) if m else h, "->", h[-60:])
    except Exception as e:
        print(f"{base}: ERROR {e}")
