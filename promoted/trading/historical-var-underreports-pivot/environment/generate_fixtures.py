#!/usr/bin/env python3
import csv
import datetime as dt
import json
import math
import random
import sys
from pathlib import Path


def discrete_var(prices, positions):
    returns = {}
    latest = {}
    for asset, observations in prices.items():
        previous = None
        series = {}
        for date, value in observations:
            if value is None:
                continue
            if previous is not None:
                series[date] = value / previous - 1.0
            previous = value
            latest[asset] = value
        returns[asset] = series
    common = set.intersection(*(set(series) for series in returns.values()))
    losses = []
    for date in sorted(common):
        pnl = sum(positions[a] * latest[a] * returns[a][date] for a in prices)
        losses.append(-pnl)
    losses.sort(reverse=True)
    k = int(math.floor((1.0 - 0.99) * len(losses)))
    return float(losses[k])


def make_book(root, name, seed, asset_count, day_count, missing_rate, shared):
    rng = random.Random(seed)
    assets = [f"A{seed % 1000:03d}_{i:03d}" for i in range(asset_count)]
    dates = [(dt.date(2015, 1, 1) + dt.timedelta(days=i)).isoformat() for i in range(day_count)]
    shared_missing = {i for i in range(3, day_count, 17)} if shared else set()
    prices = {}
    for index, asset in enumerate(assets):
        value = 35.0 + index * 1.7 + rng.random() * 10.0
        observations = []
        for day, date in enumerate(dates):
            missing = day in shared_missing if shared else (day > 0 and rng.random() < missing_rate)
            if missing:
                observations.append((date, None))
                continue
            value *= 1.0 + rng.gauss(0.0002, 0.014 + (index % 5) * 0.001)
            observations.append((date, round(value, 8)))
        prices[asset] = observations
    positions = {asset: ((-1) ** i) * (17 + (i * 13) % 83) for i, asset in enumerate(assets)}
    out = root / name
    out.mkdir(parents=True, exist_ok=True)
    with (out / "prices.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", *assets])
        for row_index, date in enumerate(dates):
            writer.writerow([date, *["" if prices[a][row_index][1] is None else prices[a][row_index][1] for a in assets]])
    with (out / "positions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["asset", "position"])
        writer.writerows((asset, positions[asset]) for asset in assets)
    with (out / "expected.json").open("w", encoding="utf-8") as handle:
        json.dump({"var_99": discrete_var(prices, positions)}, handle)


def main(output):
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    make_book(root, "sample", 311, 5, 72, 0.0, True)
    make_book(root, "sample_staggered", 733, 7, 140, 0.055, False)
    make_book(root, "sample_prod", 1907, 250, 2500, 0.002, False)
    (root / "sample_prod" / "expected.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main(sys.argv[1])
