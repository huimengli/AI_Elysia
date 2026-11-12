# -*- coding: utf-8 -*-
"""Dump raw simple-index HTML for jieba/jieba_fast (head)."""
import urllib.request

for pkg in ("jieba", "jieba_fast"):
    url = f"https://pypi.tuna.tsinghua.edu.cn/simple/{pkg}/"
    data = urllib.request.urlopen(url, timeout=30).read()
    text = data.decode("utf-8", "ignore")
    print("=" * 20, pkg, "bytes:", len(data))
    print(text[:1500])
