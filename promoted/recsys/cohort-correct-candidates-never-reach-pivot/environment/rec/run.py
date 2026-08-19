import csv
from pathlib import Path

from .features import assemble_features
from .rank import score
from .retrieval import retrieve, users


def main():
    output = Path("/app/output/recommendations.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["user_id", "item_id", "rank"])
        for user in users():
            rows = assemble_features(user["user_id"], retrieve(user["user_id"]))
            rows.sort(key=lambda row: (-score(row), int(str(row["item_id"]).lstrip("0") or "0")))
            for rank, row in enumerate(rows[:10], 1):
                item_id = int(str(row["item_id"]).lstrip("0") or "0")
                writer.writerow([user["user_id"], item_id, rank])


if __name__ == "__main__":
    main()
