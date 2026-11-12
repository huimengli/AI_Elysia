"""Fetch openWakeWord repo tree via jsDelivr; dump full tree; download selected files (tolerant)."""
import json
import os
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://data.jsdelivr.com/v1/packages/gh/dscripka/openWakeWord@main"
CDN = "https://cdn.jsdelivr.net/gh/dscripka/openWakeWord@main/"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    tree = json.loads(get(BASE))
    files = []

    def walk(node, prefix=""):
        for f in node.get("files", []):
            p = prefix + "/" + f["name"] if prefix else f["name"]
            if f.get("type") == "directory":
                walk(f, p)
            else:
                files.append((p, f.get("size") or 0))

    walk(tree)
    with open("_oww_tree.txt", "w", encoding="utf-8") as fh:
        for p, s in files:
            fh.write(f"{p}\t{s}\n")
    print(f"total_files={len(files)} tree -> _oww_tree.txt")

    want = [p for p, s in files if p.startswith("train/") and (p.endswith(".py") or p.endswith(".yaml") or p.endswith(".txt"))]
    extra = [p for p, s in files if p in ("README.md", "requirements.txt")]
    want += extra

    ok, fail = 0, []
    for p in want:
        dest = p.replace("/", os.sep)
        d = os.path.dirname(dest)
        if d:
            os.makedirs(d, exist_ok=True)
        try:
            data = get(CDN + p)
            with open(dest, "wb") as fh:
                fh.write(data)
            print(f"OK {p} ({len(data)} bytes)")
            ok += 1
        except Exception as e:
            fail.append(p)
            print(f"FAIL {p}: {e}")
    print(f"DONE ok={ok} fail={len(fail)}")
    if fail:
        with open("_oww_fail.txt", "w", encoding="utf-8") as fh:
            fh.write("\n".join(fail))


if __name__ == "__main__":
    main()
