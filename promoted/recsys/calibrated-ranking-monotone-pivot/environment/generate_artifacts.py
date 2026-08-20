#!/usr/bin/env python3
import json
import struct
import sys
from pathlib import Path

WEIGHTS = {0: 1.3, 1: 0.7, 2: 1.1, 3: 0.9, 4: 1.5, 5: 0.6, 6: 1.2, 7: 0.8}
ENCOUNTER_ORDER = [4, 0, 7, 2, 5, 1, 6, 3]


def main(output_dir):
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    records = [(bucket_id, WEIGHTS[bucket_id]) for bucket_id in ENCOUNTER_ORDER]
    with (root / "calibration.bin").open("wb") as handle:
        handle.write(struct.pack("<4sII", b"CALB", 1, len(records)))
        for bucket_id, weight in records:
            handle.write(struct.pack("<id", bucket_id, weight))
    (root / "calibration.json").write_text(
        json.dumps([{"bucket_id": bucket_id, "weight": weight} for bucket_id, weight in records], indent=2)
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main(sys.argv[1])

