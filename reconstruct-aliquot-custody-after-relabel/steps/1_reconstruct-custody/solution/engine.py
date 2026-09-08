from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path

from .io import read_jsonl


RECEIPT_FIELDS = (
    "command_digest",
    "execution_id",
    "input_position_id",
    "output_position_id",
    "quantity_ul",
)


def _unique(rows: list[dict], field: str, source: str) -> None:
    values = [row[field] for row in rows]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {field} in {source}")


def _edge_key(edge: dict) -> tuple:
    return (
        edge["edge_type"],
        edge["from_node_id"],
        edge["to_node_id"],
        edge["quantity_ul"],
        "" if edge["receipt_id"] is None else edge["receipt_id"],
    )


def _base(case_dir: Path) -> tuple[dict, list[dict], list[dict]]:
    nodes = read_jsonl(case_dir, "physical_nodes.jsonl")
    operations = read_jsonl(case_dir, "operations.jsonl")
    receipts = read_jsonl(case_dir, "receipts.jsonl")
    results = read_jsonl(case_dir, "results.jsonl")
    _unique(nodes, "node_id", "physical_nodes.jsonl")
    _unique(operations, "operation_id", "operations.jsonl")
    _unique(receipts, "receipt_id", "receipts.jsonl")
    _unique(results, "result_id", "results.jsonl")

    node_by_id = {row["node_id"]: row for row in nodes}
    operations_by_binding: dict[tuple, list[dict]] = defaultdict(list)
    for operation in operations:
        if operation.get("successful") is True:
            binding = tuple(operation[field] for field in RECEIPT_FIELDS)
            operations_by_binding[binding].append(operation)

    physical_edges: list[dict] = []
    used_operations: set[str] = set()
    for receipt in receipts:
        binding = tuple(receipt[field] for field in RECEIPT_FIELDS)
        matches = operations_by_binding.get(binding, [])
        if len(matches) != 1:
            raise ValueError(f"receipt {receipt['receipt_id']} does not bind one successful execution")
        operation = matches[0]
        if operation["operation_id"] in used_operations:
            raise ValueError("more than one receipt authorizes an operation")
        used_operations.add(operation["operation_id"])
        if operation["edge_type"] != "physical_material":
            raise ValueError("robot receipts may authorize only physical material")
        if operation["input_node_id"] not in node_by_id or operation["output_node_id"] not in node_by_id:
            raise ValueError("operation refers to an unknown physical node")
        physical_edges.append(
            {
                "edge_type": "physical_material",
                "from_node_id": operation["input_node_id"],
                "to_node_id": operation["output_node_id"],
                "quantity_ul": operation["quantity_ul"],
                "receipt_id": receipt["receipt_id"],
            }
        )

    outgoing: dict[str, int] = defaultdict(int)
    incoming: dict[str, int] = defaultdict(int)
    children: dict[str, list[str]] = defaultdict(list)
    for edge in physical_edges:
        quantity = edge["quantity_ul"]
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0:
            raise ValueError("physical quantities must be nonnegative integers")
        outgoing[edge["from_node_id"]] += quantity
        incoming[edge["to_node_id"]] += quantity
        children[edge["from_node_id"]].append(edge["to_node_id"])

    for node in nodes:
        quantities = [node[name] for name in ("initial_quantity_ul", "retained_quantity_ul", "consumed_quantity_ul")]
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in quantities):
            raise ValueError("node quantities must be nonnegative integers")
        expected = node["retained_quantity_ul"] + node["consumed_quantity_ul"] + outgoing[node["node_id"]]
        if node["initial_quantity_ul"] != expected:
            raise ValueError(f"conservation failure at {node['node_id']}")
        if node["node_kind"] != "specimen" and incoming[node["node_id"]] != node["initial_quantity_ul"]:
            raise ValueError(f"incoming quantity mismatch at {node['node_id']}")

    tainted: set[str] = {node["node_id"] for node in nodes if node.get("tainted_initial") is True}
    queue = deque(tainted)
    while queue:
        parent = queue.popleft()
        for child in children[parent]:
            if child not in tainted:
                tainted.add(child)
                queue.append(child)

    analytical_edges: list[dict] = []
    originals: list[dict] = []
    for result in results:
        if result["physical_node_id"] not in node_by_id:
            raise ValueError("result refers to an unknown physical node")
        analytical_edges.append(
            {
                "edge_type": "analytical_derivation",
                "from_node_id": result["physical_node_id"],
                "to_node_id": result["result_id"],
                "quantity_ul": 0,
                "receipt_id": None,
            }
        )
        if result.get("rerun_id") is None:
            originals.append(result)

    report = {
        "custody_edges": sorted(physical_edges + analytical_edges, key=_edge_key),
        "authoritative_result_ids": sorted(row["result_id"] for row in originals),
        "tainted_physical_node_ids": sorted(tainted),
    }
    return report, nodes, results


def build_report(case_dir: Path) -> dict:
    report, nodes, results = _base(case_dir)
    try:
        from .reruns import apply_reruns
    except ImportError:
        apply_reruns = None
    if apply_reruns is not None:
        report = apply_reruns(case_dir, report, nodes, results)
    try:
        from .recall import apply_recall
    except ImportError:
        apply_recall = None
    if apply_recall is not None:
        report = apply_recall(case_dir, report, nodes, results)
    return report
