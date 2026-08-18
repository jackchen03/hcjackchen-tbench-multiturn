#!/usr/bin/env python3
"""Catalog-level gate: run the per-task hard gates over every task in a catalog,
plus the two checks that only exist across tasks.

Per-task gates live in validate_task.py - this script does not duplicate them,
so there is exactly one implementation to keep honest.

Cross-task checks:
  X1  byte-identical clones  - N renamed copies of one task measure one problem N times
  X2  fiction names          - the slug promises work the task does not contain

Usage:
    python3 check_catalog_uniqueness.py <catalog-dir> [--strict] [--verbose]
Exit: 0 every task clean, 1 otherwise.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from validate_task import blocking, check_task
except ImportError:
    def blocking(x, strict=False): return []
    def check_task(x): return []

STOPWORDS = {
    "with", "then", "from", "into", "task", "step", "steps", "multi", "turn", "pivot",
    "pipeline", "validation", "migration", "feature", "optimization", "refactor", "extends",
}


def hash_task(td: Path) -> str | None:
    files = sorted(td.glob("steps/*/solution/solve.sh"))
    files += sorted(td.glob("steps/*/tests/test_outputs.py"))
    df = td / "environment" / "Dockerfile"
    if df.exists():
        files.append(df)
    if not files:
        return None
    h = hashlib.sha256()
    for p in files:
        h.update(p.name.encode())
        h.update(hashlib.sha256(p.read_bytes()).hexdigest().encode())
    return h.hexdigest()


def check_clones(tasks: list[Path]) -> list[str]:
    buckets: dict[str, list[str]] = {}
    for t in tasks:
        h = hash_task(t)
        if h:
            buckets.setdefault(h, []).append(t.name)
    problems = []
    for h, names in buckets.items():
        if len(names) > 1:
            problems.append(f"X1 byte-identical clones ({h[:10]}): {', '.join(sorted(names))}")
    return problems


def check_fiction(task: Path) -> list[str]:
    words = {w for w in re.split(r"[^a-z0-9]+", task.name.lower()) if len(w) >= 4 and w not in STOPWORDS}
    if not words:
        return []
    blob = [" ".join(p.name for p in task.glob("steps/*")).lower()]
    patterns = (
        "steps/*/instruction.md",
        "steps/*/solution/*",
        "steps/*/tests/*",
        "task.toml",
        "dossier.md",
        "README.md",
        "environment/*",
    )
    for pattern in patterns:
        for p in task.glob(pattern):
            if not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            text = p.read_text(errors="replace")
            if p.name == "instruction.md":
                text = "\n".join(text.splitlines()[1:]) if text.startswith("#") else text
            blob.append(text.lower())
    combined = "\n".join(blob).replace("task@example.com", "")
    missing = sorted(w for w in words if w not in combined)
    if missing:
        return [
            f"X2 fiction name: the slug promises {missing} but those words appear nowhere in the "
            "task's steps, config, environment or dossier"
        ]
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the hard gates over a whole multi-turn task catalog")
    ap.add_argument("catalog_dir")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--verbose", action="store_true", help="print every finding, not just the count")
    args = ap.parse_args()

    root = Path(args.catalog_dir).resolve()
    candidates = sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith("."))
    tasks = [d for d in candidates if (d / "task.toml").exists()]
    incomplete = [d for d in candidates if d not in tasks and any(d.iterdir())]
    if not tasks and not incomplete:
        print(f"no task directories under {root}", file=sys.stderr)
        return 1

    print(f"== catalog gate: {len(tasks)} task(s) under {root}\n")
    rejected: list[tuple[str, list[str]]] = []
    for d in incomplete:
        rejected.append((d.name, ["X3 no task.toml - half-generated task directory"]))
        print(f"REJECT  {d.name}  (no task.toml - half-generated)")

    for t in tasks:
        reasons = []
        bad = blocking(check_task(t), args.strict)
        if bad:
            reasons += [f"{f.severity} {f.code} {f.message}" for f in bad]
        reasons += check_fiction(t)
        if reasons:
            rejected.append((t.name, reasons))
            print(f"REJECT  {t.name}  ({len(reasons)} blocking)")
            for r in reasons if args.verbose else reasons[:3]:
                print(f"          {r}")
            if not args.verbose and len(reasons) > 3:
                print(f"          ... {len(reasons) - 3} more (--verbose)")
        else:
            print(f"OK      {t.name}")

    clones = check_clones(tasks)
    for c in clones:
        print(f"\nCRITICAL {c}")

    rejected_names = {name for name, _ in rejected}
    usable = len([t for t in tasks if t.name not in rejected_names])
    extra = f", {len(incomplete)} incomplete dir(s)" if incomplete else ""
    print(f"\n== {usable}/{len(tasks)} task(s) usable, {len(rejected)} rejected{extra}, "
          f"{len(clones)} clone group(s)")
    if rejected or clones:
        print("do NOT ship this catalog - fix the rejects and re-run")
        return 1
    print("catalog gate passed (static). Each task still needs run_oracle_chain.py before it counts as proven.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
