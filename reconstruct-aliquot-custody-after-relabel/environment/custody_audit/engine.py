"""Incomplete incident evaluator using unreliable display fields."""

from __future__ import annotations

from pathlib import Path

from .io import read_jsonl


def build_report(case_dir: Path) -> dict:
    operations = read_jsonl(case_dir, "operations.jsonl")
    latest_by_barcode: dict[str, dict] = {}
    for operation in operations:
        barcode = operation.get("output_barcode")
        if barcode is None:
            continue
        if operation.get("sequence_counter", -1) >= latest_by_barcode.get(barcode, {}).get(
            "sequence_counter", -1
        ):
            latest_by_barcode[barcode] = operation
    edges = [
        {
            "edge_type": row["edge_type"],
            "from_node_id": row["input_node_id"],
            "to_node_id": row["output_node_id"],
            "quantity_ul": row["quantity_ul"],
            "receipt_id": None,
        }
        for row in latest_by_barcode.values()
        if row.get("successful")
    ]
    return {
        "custody_edges": sorted(edges, key=lambda item: tuple(str(item[k]) for k in sorted(item))),
        "authoritative_result_ids": [],
        "tainted_physical_node_ids": [],
    }
