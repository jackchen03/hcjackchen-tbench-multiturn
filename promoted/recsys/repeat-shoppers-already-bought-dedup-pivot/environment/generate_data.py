#!/usr/bin/env python3
import sys
from pathlib import Path

import pandas as pd


def main(output):
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    catalog = []
    for product_id in range(1, 61):
        for variant in range(2):
            catalog.append({"sku": 100000 + product_id * 10 + variant, "product_id": product_id})
    pd.DataFrame(catalog).to_parquet(root / "catalog.parquet", index=False)

    cf = []
    pop = []
    purchases = []
    for user_id in range(1, 5):
        bought = range(1, 7) if user_id <= 2 else range(1, 2)
        purchases.extend({"user_id": user_id, "item_id": product_id} for product_id in bought)
        for product_id in range(1, 46):
            sku = 100000 + product_id * 10
            score = 1000.0 - product_id * 3.0 - user_id / 100.0
            cf.append({"user_id": user_id, "item_id": sku, "score": score})
            if product_id <= 15:
                pop.append({"user_id": user_id, "item_id": f"{sku:07d}", "score": score - 0.5})
            if product_id <= 12:
                variant = sku + 1
                pop.append({"user_id": user_id, "item_id": f"{variant:07d}", "score": score - 1.0})
    pd.DataFrame(cf).to_parquet(root / "cand_cf.parquet", index=False)
    pd.DataFrame(pop).to_parquet(root / "cand_pop.parquet", index=False)
    pd.DataFrame(purchases).to_parquet(root / "purchases.parquet", index=False)


if __name__ == "__main__":
    main(sys.argv[1])
