#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def proportional(caps, quantity, orders):
    quantity = min(quantity, sum(caps))
    if quantity <= 0:
        return [0] * len(caps)
    total = sum(caps)
    allocations = [cap * quantity // total for cap in caps]
    left = quantity - sum(allocations)
    priority = sorted(
        range(len(caps)),
        key=lambda index: (-(caps[index] * quantity % total), orders[index]["seq"], orders[index]["order_id"]),
    )
    for index in priority:
        if left == 0:
            break
        if allocations[index] < caps[index]:
            allocations[index] += 1
            left -= 1
    return allocations


def reference(event):
    orders = sorted(event["resting_orders"], key=lambda order: (order["seq"], order["order_id"]))
    total_fill = min(event["incoming_qty"], sum(order["qty"] for order in orders))
    if total_fill == sum(order["qty"] for order in orders):
        fills = [order["qty"] for order in orders]
    else:
        carve = min(orders[0]["qty"], (total_fill + 1) // 2)
        caps = [order["qty"] for order in orders]
        caps[0] -= carve
        fills = proportional(caps, total_fill - carve, orders)
        fills[0] += carve
    return [{"order_id": order["order_id"], "filled_qty": fill} for order, fill in zip(orders, fills)]


def order(order_id, participant_id, seq, qty):
    return {"order_id": order_id, "participant_id": participant_id, "price": 100, "seq": seq, "qty": qty}


def main(output_path):
    events = [
        {"event_id": "sample-1", "incoming_qty": 10, "resting_orders": [order("A1", "P1", 1, 6), order("A2", "P2", 2, 6), order("A3", "P3", 3, 8)]},
        {"event_id": "sample-2", "incoming_qty": 7, "resting_orders": [order("B1", "P1", 1, 2), order("B2", "P2", 2, 5), order("B3", "P3", 3, 7)]},
        {"event_id": "sample-3", "incoming_qty": 20, "resting_orders": [order("C1", "P3", 1, 20), order("C2", "P1", 2, 20), order("C3", "P2", 3, 20)]},
        {"event_id": "sample-4", "incoming_qty": 13, "resting_orders": [order("D1", "P2", 1, 4), order("D2", "P1", 2, 10), order("D3", "P3", 3, 12)]},
        {"event_id": "sample-5", "incoming_qty": 18, "resting_orders": [order("E1", "P4", 1, 8), order("E2", "P3", 2, 12), order("E3", "P2", 3, 16), order("E4", "P1", 4, 20)]},
    ]
    for event in events:
        event["reference_fills"] = reference(event)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(events, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
