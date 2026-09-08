from __future__ import annotations

import json
from pathlib import Path


def read_jsonl(case_dir: Path, name: str) -> list[dict]:
    path = case_dir / name
    if not path.exists():
        return []
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{name}:{line_number}: object required")
        rows.append(value)
    return rows
