#!/usr/bin/env python3
import subprocess
from pathlib import Path

samples = {
    "names-1.txt": ["README.TXT", "readme.txt", "MixedCase.doc"],
    "names-2.txt": ["FileOneLong.txt", "AlphaThingLong.bin", "GammaStuffLong.dat"],
    "names-3.txt": ["collision-name-one.txt", "collision name one.txt", "collision.name.one.txt"],
    "names-4.txt": ["Quarterly Report 2026.pdf", "resume-final.doc"],
}
root = Path("/generated/samples")
root.mkdir(parents=True, exist_ok=True)
for filename, names in samples.items():
    path = root / filename
    path.write_text("\n".join(names) + "\n", encoding="utf-8")
    subprocess.run(["/build/vfatdir", str(path), str(root / filename.replace("names", "dir").replace(".txt", ".bin"))], check=True)
