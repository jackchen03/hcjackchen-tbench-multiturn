from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import build_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="custody_audit")
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = build_report(args.case_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
