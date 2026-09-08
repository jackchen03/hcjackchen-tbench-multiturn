def operand_width(value):
    value = abs(int(value))
    if value <= 0x7F:
        return 1
    if value <= 0x7FFF:
        return 2
    return 3


def base_width(op):
    if op["op"] == "marker":
        return 0
    prefix = 1 if op.get("prefix") else 0
    if op["op"] in {"set", "add", "mul"}:
        return 1 + prefix + operand_width(op.get("arg", 0))
    if op["op"] == "branch_if_lt":
        return 2 + prefix + operand_width(op.get("arg", 0))
    return 1 + prefix


def final_layout(ops):
    """Converge offsets and branch displacement widths."""
    sizes = [base_width(op) for op in ops]
    for _ in range(16):
        offsets, cursor = [], 0
        for size in sizes:
            offsets.append(cursor)
            cursor += size
        labels = {op["label"]: offsets[i] for i, op in enumerate(ops) if "label" in op}
        changed = False
        for i, op in enumerate(ops):
            if op["op"] != "branch_if_lt":
                continue
            delta = labels[op["target"]] - (offsets[i] + sizes[i])
            wanted = 1 + (1 if op.get("prefix") else 0) + operand_width(op.get("arg", 0)) + operand_width(delta)
            if wanted != sizes[i]:
                sizes[i] = wanted
                changed = True
        if not changed:
            return offsets, sizes
    raise ValueError("branch layout did not converge")
