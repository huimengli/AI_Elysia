# -*- coding: utf-8 -*-
"""Dump char codes of the Q3 line in records for exact-match debugging."""
lines = open(r"C:\Users\楼听\Desktop\git\JarvisAi\records\2026-10-13-11-55.md",
             encoding="utf-8").read().splitlines()
for i, ln in enumerate(lines, 1):
    if "Q3" in ln:
        print("line", i)
        for ch in ln:
            print(f"U+{ord(ch):04X} {ch!r}")
