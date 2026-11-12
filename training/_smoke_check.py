import wave
from pathlib import Path

d = Path("openWakeWord/output/_smoke")
for f in sorted(d.glob("*.wav")):
    with wave.open(str(f), "rb") as w:
        print(f.name, w.getframerate(), round(w.getnframes() / w.getframerate(), 2), "s", f.stat().st_size, "bytes")
