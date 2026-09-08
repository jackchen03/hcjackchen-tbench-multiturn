from __future__ import annotations

import base64
import json
import os
import subprocess
import tempfile
from collections import defaultdict, deque
from pathlib import Path

from .io import read_jsonl


def _canonical_rerun(row: dict) -> bytes:
    lines = ["CUSTODY-RERUN-SCOPE-V1", f"rerun={row['rerun_id']}", f"root={row['root_node_id']}"]
    lines.extend(f"node={value}" for value in row["node_ids"])
    lines.extend(f"boundary={value}" for value in row["boundary_node_ids"])
    lines.extend(f"supersedes={value}" for value in row["supersedes"])
    return ("\n".join(lines) + "\n").encode("utf-8")


def _canonical_revocation(row: dict) -> bytes:
    return (
        "CUSTODY-RERUN-REVOCATION-V1\n"
        f"revocation={row['revocation_id']}\n"
        f"rerun={row['rerun_id']}\n"
    ).encode("utf-8")


def _load_issuers(case_dir: Path) -> dict:
    path = case_dir / "issuers.json"
    if not path.exists():
        path = Path("/app/keys/issuers.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("issuers.json must be an object")
    return value


def _verify(row: dict, payload: bytes, role: str, issuers: dict) -> None:
    issuer = issuers.get(row["issuer_id"])
    if not isinstance(issuer, dict) or role not in issuer.get("roles", []):
        raise ValueError("unauthorized signed record issuer")
    try:
        public_raw = base64.b64decode(issuer["public_key_b64"], validate=True)
        signature = base64.b64decode(row["signature"], validate=True)
        if len(public_raw) != 32 or len(signature) != 64:
            raise ValueError("invalid Ed25519 material")
        with tempfile.TemporaryDirectory(prefix="custody-signature-", dir=os.environ.get("HOME", "/tmp")) as tmp:
            tmp_path = Path(tmp)
            public_der = bytes.fromhex("302a300506032b6570032100") + public_raw
            (tmp_path / "public.der").write_bytes(public_der)
            (tmp_path / "message").write_bytes(payload)
            (tmp_path / "signature").write_bytes(signature)
            checked = subprocess.run(
                ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(tmp_path / "public.der"), "-keyform", "DER", "-rawin", "-in", str(tmp_path / "message"), "-sigfile", str(tmp_path / "signature")],
                capture_output=True,
                timeout=5,
            )
            if checked.returncode != 0:
                raise ValueError("signature verification failed")
    except (ValueError, KeyError, subprocess.SubprocessError) as error:
        raise ValueError("invalid signed record") from error


def _reachable(root: str, boundaries: set[str], adjacency: dict[str, list[str]]) -> set[str]:
    seen = {root}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        for child in adjacency[current]:
            if child in boundaries or child in seen:
                continue
            seen.add(child)
            queue.append(child)
    return seen


def apply_reruns(case_dir: Path, report: dict, nodes: list[dict], results: list[dict]) -> dict:
    reruns = read_jsonl(case_dir, "reruns.jsonl")
    revocations = read_jsonl(case_dir, "revocations.jsonl")
    if len({row["rerun_id"] for row in reruns}) != len(reruns):
        raise ValueError("duplicate rerun ID")
    if len({row["revocation_id"] for row in revocations}) != len(revocations):
        raise ValueError("duplicate revocation ID")
    issuers = _load_issuers(case_dir)

    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in report["custody_edges"]:
        if edge["edge_type"] in {"physical_material", "analytical_derivation"}:
            adjacency[edge["from_node_id"]].append(edge["to_node_id"])

    valid: dict[str, dict] = {}
    for row in reruns:
        for field in ("node_ids", "boundary_node_ids", "supersedes"):
            values = row[field]
            if values != sorted(set(values)):
                raise ValueError(f"{field} must be sorted and unique")
        _verify(row, _canonical_rerun(row), "rerun_authority", issuers)
        reachable = _reachable(row["root_node_id"], set(row["boundary_node_ids"]), adjacency)
        if not set(row["node_ids"]).issubset(reachable):
            raise ValueError("rerun scope names a node outside its bounded descendants")
        valid[row["rerun_id"]] = row

    revoked: set[str] = set()
    for row in revocations:
        _verify(row, _canonical_revocation(row), "revocation_authority", issuers)
        revoked.add(row["rerun_id"])
    active = {rerun_id: row for rerun_id, row in valid.items() if rerun_id not in revoked}

    def outranks(left: str, right: str) -> bool:
        seen: set[str] = set()
        stack = list(active[left]["supersedes"])
        while stack:
            value = stack.pop()
            if value == right:
                return True
            if value in seen:
                continue
            seen.add(value)
            if value in active:
                stack.extend(active[value]["supersedes"])
        return False

    originals = {row["result_id"]: row for row in results if row.get("rerun_id") is None}
    replacements: dict[str, list[dict]] = defaultdict(list)
    for result in results:
        rerun_id = result.get("rerun_id")
        original_id = result.get("original_result_id")
        if rerun_id not in active or original_id not in originals:
            continue
        scope = set(active[rerun_id]["node_ids"])
        original = originals[original_id]
        if result["physical_node_id"] in scope and original_id in scope and original["physical_node_id"] in scope:
            replacements[original_id].append(result)

    authority: list[dict] = []
    authority_edges: list[dict] = []
    current_ids: list[str] = []
    for original_id in sorted(originals):
        candidates = replacements[original_id]
        winners = [
            row
            for row in candidates
            if all(row["rerun_id"] == other["rerun_id"] or outranks(row["rerun_id"], other["rerun_id"]) for other in candidates)
        ]
        if len(winners) == 1:
            chosen = winners[0]
            current_id = chosen["result_id"]
            rerun_id = chosen["rerun_id"]
            authority_edges.append(
                {
                    "edge_type": "result_authority",
                    "from_node_id": original_id,
                    "to_node_id": current_id,
                    "quantity_ul": 0,
                    "receipt_id": None,
                }
            )
        else:
            current_id = original_id
            rerun_id = None
        current_ids.append(current_id)
        authority.append(
            {
                "original_result_id": original_id,
                "authoritative_result_id": current_id,
                "authority_rerun_id": rerun_id,
            }
        )

    report = dict(report)
    report["custody_edges"] = sorted(
        report["custody_edges"] + authority_edges,
        key=lambda edge: (
            edge["edge_type"], edge["from_node_id"], edge["to_node_id"], edge["quantity_ul"], edge["receipt_id"] or ""
        ),
    )
    report["authoritative_result_ids"] = sorted(current_ids)
    report["result_authority"] = authority
    return report
