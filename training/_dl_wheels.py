"""Temp: download torchinfo + torchmetrics wheels from Tsinghua mirror (pip index stalls silently)."""
import os
import re
import subprocess
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"


def _ver_tuple(href: str):
    # wheel name: <name>-<version>-<pytag>-<abitag>-<platform>.whl (name may contain _ )
    fn = href.split("#")[0]
    parts = re.sub(r"\.(whl|tar\.gz)$", "", fn).split("-")
    v = parts[1]
    nums = []
    for tok in v.split(".")[:3]:
        m = re.match(r"(\d+)", tok)
        nums.append(int(m.group(1)) if m else 0)
    return tuple(nums)


def pick_wheel(name: str) -> str:
    url = f"{MIRROR}/{name}/"
    with urllib.request.urlopen(url, timeout=30) as r:
        html = r.read().decode("utf-8", errors="replace")
    hrefs = re.findall(r'href="([^"]+\.(?:whl|tar\.gz))', html)

    def _is_prel(h: str) -> bool:
        base = h.split("#")[0].split("/")[-1]
        m = re.match(r"^(?:[^-]+)-(\d[\w.]*)-", base + "-")
        v = m.group(1) if m else ""
        return bool(re.search(r"(?:rc|a|b|dev|alpha|beta)\d*", v, re.I))

    hrefs = [h for h in hrefs if not _is_prel(h)]
    if not hrefs:
        raise SystemExit(f"no distribution found for {name}")
    wheels = [h for h in hrefs if ".whl" in h]
    py_ok = [h for h in wheels if "-cp312-" in h or "-py3-" in h or "-py2.py3-" in h]
    win_ok = [h for h in py_ok if ("win_amd64" in h) or ("py3-none-any" in h)]
    pure = [h for h in win_ok if "py3-none-any" in h]
    pool = pure or win_ok
    if not pool:
        pool = [h for h in hrefs if ".tar.gz" in h]
    best = max(pool, key=_ver_tuple)
    return f"{MIRROR}/{name}/{best.split('#')[0]}"


def main() -> None:
    urls = [(n, pick_wheel(n)) for n in (
        "lightning_utilities", "setuptools", "torchinfo", "torchmetrics",
        "pronouncing", "cmudict",
        "mutagen", "acoustics", "hyperpyyaml", "editdistance",
        "audioread", "lazy_loader", "msgpack", "decorator",
        "llvmlite", "numba", "soxr", "soundfile", "librosa",
        "torchaudio", "speechbrain", "audiomentations", "torch_audiomentations",
    )]
    files = []
    for name, u in urls:
        fn = f"_wheels/{u.rsplit('/', 1)[-1]}"
        os.makedirs("_wheels", exist_ok=True)
        if os.path.exists(fn) and os.path.getsize(fn) > 0:
            print(f"SKIP {fn} (already downloaded)", flush=True)
            files.append(fn)
            continue
        print(f"GET {u}", flush=True)
        with urllib.request.urlopen(u, timeout=60) as r, open(fn, "wb") as f:
            f.write(r.read())
        print(f"  -> {fn} ({os.path.getsize(fn)} bytes)", flush=True)
        files.append(fn)
    files = [f for f in files if "acoustics" not in f]  # sdist installed separately with --no-build-isolation
    # install locally, no index, no deps (train.py only needs the two packages)
    cmd = [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", *files]
    print("RUN", " ".join(cmd), flush=True)
    rc = subprocess.call(cmd)
    print(f"pip rc={rc}", flush=True)
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
