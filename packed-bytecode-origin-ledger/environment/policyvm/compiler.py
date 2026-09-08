import json
from .layout import final_layout


def _record(op):
    return {
        "origin": str(op.get("origin", op["id"])),
        "handler": op.get("handler"),
        "roots": sorted(str(x) for x in op.get("roots", [])),
    }


def _build_semantics(ops, offsets):
    # Metadata was emitted by older passes before operand widths converged.
    provisional = {}
    cursor = 0
    for op in ops:
        if op["op"] != "marker":
            provisional[cursor + (1 if op.get("prefix") else 0)] = _record(op)
        cursor += 0 if op["op"] == "marker" else 2 + (1 if op.get("prefix") else 0)
    semantics = {}
    for op, offset in zip(ops, offsets):
        record = provisional.get(offset + (1 if op.get("prefix") else 0))
        if record is not None:
            semantics[op["id"]] = record
    return semantics


def _phase(op, labels):
    phase = {"id": op["id"], "op": op["op"]}
    if "arg" in op:
        phase["arg"] = int(op["arg"])
    if op["op"] == "branch_if_lt":
        phase["target_index"] = labels[op["target"]]
        phase["target_label"] = op["target"]
    return phase


def _group_ops(ops):
    groups = []
    i = 0
    while i < len(ops):
        token = ops[i].get("fuse")
        if token is None:
            groups.append([ops[i]])
            i += 1
            continue
        j = i + 1
        while j < len(ops) and ops[j].get("fuse") == token:
            j += 1
        groups.append(ops[i:j])
        i = j
    return groups


def _visible_ids(group, semantics):
    seen = set()
    visible = []
    for op in group:
        rec = semantics.get(op["id"], {})
        origin = rec.get("origin")
        if origin not in seen:
            seen.add(origin)
            visible.append(op["id"])
    return visible


def _encoded_size(instructions, semantics):
    stream = sum(item["encoded_bytes"] for item in instructions)
    table = 0
    used = {phase_id for item in instructions for phase_id in item["visible_ids"]}
    for phase_id in used:
        rec = semantics.get(phase_id, {"origin": "", "handler": None, "roots": []})
        table += 2 + len(rec["origin"].encode())
        table += 0 if rec["handler"] is None else 1 + len(str(rec["handler"]).encode())
        table += sum(1 + len(root.encode()) for root in rec["roots"])
    return stream + table


def compile_program(program):
    ops = [dict(op) for op in program["ops"]]
    ids = [op["id"] for op in ops]
    if len(set(ids)) != len(ids):
        raise ValueError("operation ids must be unique")
    offsets, sizes = final_layout(ops)
    labels = {op["label"]: i for i, op in enumerate(ops) if "label" in op}
    semantics = _build_semantics(ops, offsets)
    instructions = []
    for group in _group_ops(ops):
        indices = [ids.index(op["id"]) for op in group]
        raw_size = sum(sizes[index] for index in indices)
        fused = len(group) > 1
        instructions.append({
            "offset": offsets[indices[0]],
            "encoded_bytes": max(1, raw_size - (len(group) - 1) * 2) if fused else raw_size,
            "fused": fused,
            "phases": [_phase(op, labels) for op in group],
            "visible_ids": _visible_ids(group, semantics),
        })
    artifact = {
        "version": 1,
        "instructions": instructions,
        "semantics": semantics,
        "max_encoded_bytes": program.get("max_encoded_bytes"),
    }
    artifact["encoded_size"] = _encoded_size(instructions, semantics)
    return artifact


def write_artifact(program_path, artifact_path):
    with open(program_path, encoding="utf-8") as src:
        program = json.load(src)
    artifact = compile_program(program)
    with open(artifact_path, "w", encoding="utf-8") as dst:
        json.dump(artifact, dst, sort_keys=True, separators=(",", ":"))
        dst.write("\n")
