# -*- coding: utf-8 -*-
"""Inspect import lines of GPT_SoVITS/AR inside the main tarball on disk."""
import io
import tarfile

TAR = r"C:\Users\楼听\Desktop\git\JarvisAi\_gsv_main.tar.gz"
with tarfile.open(TAR) as tf:
    for m in tf.getmembers():
        if (m.name.startswith("GPT-SoVITS-main/GPT_SoVITS/AR/")
                and m.name.endswith(".py")):
            f = tf.extractfile(m)
            text = io.TextIOWrapper(f, encoding="utf-8").read()
            for ln in text.splitlines():
                s = ln.strip()
                if s.startswith(("import ", "from ")):
                    print(m.name.split("GPT-SoVITS-main/")[-1], "::", s)
