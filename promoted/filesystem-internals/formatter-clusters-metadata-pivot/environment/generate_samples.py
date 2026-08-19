#!/usr/bin/env python3
import subprocess
from pathlib import Path

output = Path("/generated/samples")
output.mkdir(parents=True, exist_ok=True)
specs = [(8, 1, 1), (12, 1, 2)]
for size, stride, flex in specs:
    subprocess.run(["/build/myfs-mkfs", str(output / f"myfs-{size}-{stride}-{flex}.img"),
                    str(size), str(stride), str(flex)], check=True)
(output / "specs.txt").write_text("".join(f"{s} {t} {f}\n" for s, t, f in specs), encoding="utf-8")
