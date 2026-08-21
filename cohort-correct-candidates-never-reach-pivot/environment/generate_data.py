#!/usr/bin/env python3
import json
from pathlib import Path

root = Path("/app/data")
root.mkdir(parents=True, exist_ok=True)
users = [{"user_id": value} for value in range(101, 107)]
candidates = {}
features = {}
affinity = {}
gold = {}
for index, user in enumerate(users, 1):
    user_id = user["user_id"]
    base = index * 1000
    rows = []
    normal = []
    backfill = []
    category = []
    for offset in range(1, 11):
        item_id = base + offset
        normal.append(item_id)
        rows.append({"item_id": item_id, "source": "primary", "leaf_category_id": 1001, "user_id": user_id})
        features[str(item_id)] = {"item_quality": 0.80 - offset * 0.001}
    for offset in range(1, 6):
        item_id = base + 100 + offset
        backfill.append(item_id)
        rows.append({"item_id": f"{item_id:08d}", "source": "backfill", "leaf_category_id": 1001, "user_id": user_id})
        features[str(item_id)] = {"item_quality": 0.95 - offset * 0.001}
    for offset in range(1, 6):
        item_id = base + 200 + offset
        category.append(item_id)
        rows.append({"item_id": item_id, "source": "primary", "leaf_category_id": 4001, "user_id": user_id})
        features[str(item_id)] = {"item_quality": 0.40 - offset * 0.001}
    candidates[str(user_id)] = rows
    affinity[str(user_id)] = {"10": 0.10, "40": 1.00}
    gold[str(user_id)] = {"top10": category + backfill, "backfill": backfill, "category": category}
(root / "users.json").write_text(json.dumps(users, sort_keys=True), encoding="utf-8")
(root / "candidates.json").write_text(json.dumps(candidates, sort_keys=True), encoding="utf-8")
(root / "item_features.json").write_text(json.dumps(features, sort_keys=True), encoding="utf-8")
(root / "affinity.json").write_text(json.dumps(affinity, sort_keys=True), encoding="utf-8")
(root / "category_hierarchy.json").write_text(json.dumps({"1001": 10, "4001": 40}, sort_keys=True), encoding="utf-8")
(root / "gold.json").write_text(json.dumps(gold, sort_keys=True), encoding="utf-8")
