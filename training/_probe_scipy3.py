"""Debug scipy simple page content."""
import re
import urllib.request

base = "https://pypi.tuna.tsinghua.edu.cn/simple/"
with urllib.request.urlopen(base + "scipy/", timeout=30) as r:
    html = r.read().decode("utf-8", errors="replace")
print("html_len:", len(html))
print("head:", html[:400].replace("\n", " "))
hrefs = re.findall(r'href="([^"]+)"', html)
print("total hrefs:", len(hrefs))
for h in hrefs[:8]:
    print("  ", h[:120])
whl = [h for h in hrefs if ".whl" in h]
gz = [h for h in hrefs if ".tar.gz" in h]
print("with .whl:", len(whl), " with .tar.gz:", len(gz))
