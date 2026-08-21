import json
import struct
from pathlib import Path

import numpy as np


def bucketize(values, edges):
    return np.digitize(values, edges).tolist()


def write_artifacts(records, binary_path, json_path):
    with Path(binary_path).open("wb") as handle:
        handle.write(struct.pack("<4sII", b"CALB", 1, len(records)))
        for bucket_id, weight in records:
            handle.write(struct.pack("<id", bucket_id, weight))
    Path(json_path).write_text(
        json.dumps([{"bucket_id": bucket_id, "weight": weight} for bucket_id, weight in records]),
        encoding="utf-8",
    )
