from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .io import read_jsonl


def apply_recall(case_dir: Path, report: dict, nodes: list[dict], results: list[dict]) -> dict:
    uses = read_jsonl(case_dir, "reagent_uses.jsonl")
    invalidations = read_jsonl(case_dir, "invalid_lots.jsonl")
    if len({row["lot_id"] for row in invalidations}) != len(invalidations):
        raise ValueError("duplicate lot invalidation")
    invalid_lots = {row["lot_id"] for row in invalidations if row.get("active") is True}
    lots_by_execution: dict[str, set[str]] = defaultdict(set)
    reagent_edges: list[dict] = []
    for row in uses:
        lots_by_execution[row["assay_execution_id"]].add(row["lot_id"])
        reagent_edges.append(
            {
                "edge_type": "reagent_use",
                "from_node_id": row["lot_id"],
                "to_node_id": row["assay_execution_id"],
                "quantity_ul": 0,
                "receipt_id": None,
            }
        )

    result_by_id = {row["result_id"]: row for row in results}
    current = report.get(
        "result_authority",
        [
            {
                "original_result_id": row["result_id"],
                "authoritative_result_id": row["result_id"],
                "authority_rerun_id": None,
            }
            for row in results
            if row.get("rerun_id") is None
        ],
    )
    recalled: list[dict] = []
    for entry in current:
        result = result_by_id[entry["authoritative_result_id"]]
        if lots_by_execution[result["assay_execution_id"]] & invalid_lots:
            recalled.append(result)

    tainted = set(report["tainted_physical_node_ids"])
    available_by_specimen: dict[str, int] = defaultdict(int)
    for node in nodes:
        if node["node_id"] not in tainted:
            available_by_specimen[node["specimen_id"]] += node["retained_quantity_ul"]

    policy_path = case_dir / "assay-minimums.json"
    if not policy_path.exists():
        policy_path = Path("/app/policies/assay-minimums.json")
    minima = json.loads(policy_path.read_text(encoding="utf-8"))
    recollect: list[dict] = []
    for specimen_id, assay_id in sorted({(row["specimen_id"], row["assay_id"]) for row in recalled}):
        minimum = minima[assay_id]
        available = available_by_specimen[specimen_id]
        if available < minimum:
            recollect.append(
                {
                    "specimen_id": specimen_id,
                    "assay_id": assay_id,
                    "minimum_volume_ul": minimum,
                    "available_volume_ul": available,
                }
            )

    report = dict(report)
    report["custody_edges"] = sorted(
        report["custody_edges"] + reagent_edges,
        key=lambda edge: (
            edge["edge_type"], edge["from_node_id"], edge["to_node_id"], edge["quantity_ul"], edge["receipt_id"] or ""
        ),
    )
    report["recall_result_ids"] = sorted(row["result_id"] for row in recalled)
    report["recollect"] = recollect
    return report
