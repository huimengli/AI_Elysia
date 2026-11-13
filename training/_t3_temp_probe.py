import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath("."))

from jarvis.tools.system import _VOL_TYPE

TEMP_DIR = os.path.abspath(".tmp/pscompile")
os.makedirs(TEMP_DIR, exist_ok=True)

head = "Add-Type -TypeDefinition @'\n" + _VOL_TYPE + "\n'@ -Language CSharp"
ps = (f"$env:TEMP='{TEMP_DIR}'; $env:TMP=$env:TEMP; " + head + "; [AudioVol]::Get(0)")

r = subprocess.run(["powershell", "-NoProfile", "-command", ps],
                   capture_output=True, text=True)
print("rc", r.returncode)
print("OUT", r.stdout.strip()[:200])
print("ERR", r.stderr.strip()[:200])
