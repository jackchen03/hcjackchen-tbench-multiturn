import json
from pathlib import Path

DATA = Path("/app/data")


def users():
    return json.loads((DATA / "users.json").read_text(encoding="utf-8"))


def retrieve(user_id):
    candidates = json.loads((DATA / "candidates.json").read_text(encoding="utf-8"))
    return candidates[str(user_id)]
