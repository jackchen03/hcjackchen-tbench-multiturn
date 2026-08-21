#!/usr/bin/env python3
"""Known-bad settlement report: AMEND deltas stay in the original bucket."""

import csv
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


def calendars():
    return {
        path.stem: {line.strip() for line in path.read_text().splitlines() if line.strip()}
        for path in Path("/app/calendars").glob("*.txt")
    }


def good(day, currencies, holidays):
    return day.weekday() < 5 and all(day.isoformat() not in holidays.get(ccy, set()) for ccy in currencies)


def spot(trade_date, bought_ccy, sold_ccy, holidays):
    current = date.fromisoformat(trade_date)
    counted = 0
    while counted < 2:
        current += timedelta(days=1)
        if good(current, {bought_ccy, sold_ccy}, holidays):
            counted += 1
    return current.isoformat()  # BUG: omits the final USD good-day gate.


def legs(state, holidays):
    value_date = spot(state["trade_date"], state["bought_ccy"], state["sold_ccy"], holidays)
    return (
        (state["counterparty"], state["bought_ccy"], value_date, int(state["bought_amount"])),
        (state["counterparty"], state["sold_ccy"], value_date, -int(state["sold_amount"])),
    )


def main(messages_path, output_path):
    holidays = calendars()
    states = {}
    buckets = defaultdict(int)
    with open(messages_path) as source:
        for raw in source:
            if not raw.strip():
                continue
            message = json.loads(raw)
            trade_id = message["trade_id"]
            if message["msg_type"] == "NEW":
                states[trade_id] = message
                for counterparty, currency, value_date, amount in legs(message, holidays):
                    buckets[counterparty, currency, value_date] += amount
            elif message["msg_type"] == "AMEND":
                old = states.get(trade_id)
                if old is None:
                    states[trade_id] = message
                    continue
                old_legs = legs(old, holidays)
                # BUG: apply amount deltas to the original buckets instead of moving
                # the complete corrected trade into its terminal buckets.
                buckets[old_legs[0][:3]] += int(message["bought_amount"]) - int(old["bought_amount"])
                buckets[old_legs[1][:3]] -= int(message["sold_amount"]) - int(old["sold_amount"])
                states[trade_id] = message
            elif message["msg_type"] == "CANCEL":
                old = states.pop(trade_id, None)
                if old is not None:
                    for counterparty, currency, value_date, amount in legs(old, holidays):
                        buckets[counterparty, currency, value_date] -= amount

    with open(output_path, "w", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["counterparty", "currency", "value_date", "net_amount"])
        for key in sorted(buckets):
            if buckets[key]:
                writer.writerow([*key, buckets[key]])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: settle.py <messages_file> <output_file>")
    main(sys.argv[1], sys.argv[2])
