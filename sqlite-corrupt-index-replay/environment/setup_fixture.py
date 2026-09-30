#!/usr/bin/env python3
"""Create the deterministic solver-visible SQLite crash fixture."""

import json
import os
import random
import sqlite3
import subprocess
import sys
from pathlib import Path

PAGE_BYTES = 4096
DURABLE_PREFIX = 100
TAIL_ROWS = 20


def build_crash(seed: int, db_path: str) -> None:
    rng = random.Random(seed)
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(db_path + suffix)
        except FileNotFoundError:
            pass
    tag = f"s{seed:03d}"
    db = sqlite3.connect(db_path, isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA wal_autocheckpoint=0")
    db.execute(
        "CREATE TABLE orders(order_id TEXT PRIMARY KEY, "
        "seq INTEGER, amount REAL, status TEXT)"
    )
    db.execute("CREATE INDEX idx_big ON orders(amount) WHERE amount > 50")
    base_ids = [f"{tag}-id-{i:04d}" for i in range(DURABLE_PREFIX)]
    rng.shuffle(base_ids)
    db.execute("BEGIN")
    for pos, order_id in enumerate(base_ids):
        db.execute(
            "INSERT INTO orders VALUES(?,?,?,?)",
            (order_id, 1, float(pos % 100), "new" if pos % 2 else "ok"),
        )
    db.execute("COMMIT")
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    db.execute("BEGIN")
    for i in range(TAIL_ROWS):
        db.execute(
            "INSERT INTO orders VALUES(?,?,?,?)",
            (f"{tag}-tail-{i:04d}", 1, round(rng.uniform(0, 49.99), 2), "ok"),
        )
    db.execute("COMMIT")
    os._exit(0)


def corrupt_index(db_path: str) -> None:
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    root_page = db.execute(
        "SELECT rootpage FROM sqlite_master WHERE name='idx_big'"
    ).fetchone()[0]
    db.close()
    raw = bytearray(Path(db_path).read_bytes())
    raw[(root_page - 1) * PAGE_BYTES + 10] ^= 0xFF
    Path(db_path).write_bytes(raw)


def make_input(path: Path, seed: int) -> None:
    rng = random.Random(1234 + seed)
    tag = f"s{seed:03d}"
    base_ids = [f"{tag}-id-{i:04d}" for i in range(DURABLE_PREFIX)]
    new_ids = [f"{tag}-new-{i:04d}" for i in range(12)]
    records = [
        {
            "order_id": order_id,
            "seq": 1,
            "amount": round(rng.uniform(0, 99), 2),
            "status": "new",
        }
        for order_id in new_ids
    ]
    correction_ids = rng.sample(base_ids, 10)
    for order_id in correction_ids:
        records.append(
            {"order_id": order_id, "seq": 2, "amount": 777.25, "status": "corrected"}
        )
    for order_id in rng.sample(new_ids, 5):
        records.append(next(dict(x) for x in records if x["order_id"] == order_id))
    for order_id in correction_ids[:3]:
        records.append(
            {"order_id": order_id, "seq": 3, "amount": 888.5, "status": "corrected2"}
        )
    rng.shuffle(records)
    lower_after_higher = next(
        row
        for row in records
        if row["order_id"] == correction_ids[0] and row["seq"] == 2
    )
    records.remove(lower_after_higher)
    records.append(lower_after_higher)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in records))


def main() -> None:
    out = Path(sys.argv[1])
    seed = int(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    db_path = str(out / "store.db")
    child = subprocess.run([sys.executable, __file__, "--child", str(seed), db_path])
    if child.returncode != 0 or not Path(db_path + "-wal").exists():
        raise SystemExit("failed to preserve the crash WAL")
    corrupt_index(db_path)
    (out / "checker.log").write_text(
        "integrity_check: *** in database main *** (index idx_big)\n"
        f"durable_rows={DURABLE_PREFIX}\n"
    )
    (out / "app.conf").write_text("synchronous=OFF\nwal_autocheckpoint=0\n")
    (out / "schema.sql").write_text(
        "CREATE TABLE orders(order_id TEXT PRIMARY KEY, seq INTEGER, amount REAL, status TEXT);\n"
        "CREATE INDEX idx_big ON orders(amount) WHERE amount > 50;\n"
    )
    make_input(out / "orders_input.jsonl", seed)
    (out / "replay.py").write_text(
        "#!/usr/bin/env python3\n"
        "import json, sqlite3, sys\n"
        "inp = sys.argv[1] if len(sys.argv) > 1 else '/app/orders_input.jsonl'\n"
        "dbpath = sys.argv[2] if len(sys.argv) > 2 else '/app/store.db'\n"
        "db = sqlite3.connect(dbpath, isolation_level=None)\n"
        "for raw in open(inp):\n"
        "    row = json.loads(raw)\n"
        "    db.execute('INSERT INTO orders VALUES(?,?,?,?)', "
        "(row['order_id'], row['seq'], row['amount'], row['status']))\n"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        build_crash(int(sys.argv[2]), sys.argv[3])
    else:
        main()
