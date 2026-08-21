#!/usr/bin/env python3
import random
import struct
import subprocess
from pathlib import Path

root = Path("/generated/samples")
root.mkdir(parents=True, exist_ok=True)
for name, count, seed in (("small", 10, 11), ("multi", 24, 29)):
    rng = random.Random(seed)
    records = [(rng.randrange(0, 7), bytes([index % 256]) * 16) for index in range(count)]
    data = b"".join(struct.pack(">Q16s", key, payload) for key, payload in records)
    source = root / f"{name}.in"
    source.write_bytes(data)
    spill = root / f"{name}.spill"
    spill.mkdir()
    with source.open("rb") as handle:
        subprocess.run(["/build/refpolysort", str(root / f"{name}.out"), str(spill)], stdin=handle, check=True)
