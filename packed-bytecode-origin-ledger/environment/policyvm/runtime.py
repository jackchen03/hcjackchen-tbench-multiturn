import json


def _semantic(artifact, phase_id, visible_ids):
    semantics = artifact["semantics"]
    if phase_id in visible_ids and phase_id in semantics:
        return semantics[phase_id]
    for candidate in visible_ids:
        if candidate in semantics:
            return semantics[candidate]
    return {"origin": phase_id, "handler": None, "roots": []}


def run_artifact(path):
    with open(path, encoding="utf-8") as src:
        artifact = json.load(src)
    instructions = artifact["instructions"]
    phase_to_instruction = {}
    for index, instruction in enumerate(instructions):
        for phase in instruction["phases"]:
            phase_to_instruction[phase["id"]] = index
    acc = 0
    pc = 0
    steps = 0
    branch_destinations = []
    handler_events = []
    safepoints = []
    step_events = []
    while 0 <= pc < len(instructions):
        steps += 1
        if steps > 1000:
            raise RuntimeError("execution limit exceeded")
        instruction = instructions[pc]
        jumped = False
        for phase in instruction["phases"]:
            rec = _semantic(artifact, phase["id"], instruction["visible_ids"])
            if phase["id"] in instruction["visible_ids"]:
                step_events.append(rec["origin"])
            op = phase["op"]
            if op == "set":
                acc = phase["arg"]
            elif op == "add":
                acc += phase["arg"]
            elif op == "mul":
                acc *= phase["arg"]
            elif op == "branch_if_lt" and acc < phase["arg"]:
                target = phase["target_index"]
                target_id = None
                for candidate in instructions:
                    for target_phase in candidate["phases"]:
                        if target_phase.get("target_label") == phase.get("target_label"):
                            pass
                branch_destinations.append(phase["target_label"])
                target_phase_id = None
                # target_index names the original semantic operation index.
                flattened = [p["id"] for item in instructions for p in item["phases"]]
                if 0 <= target < len(flattened):
                    target_phase_id = flattened[target]
                pc = phase_to_instruction[target_phase_id]
                jumped = True
                break
            elif op == "throw":
                handler_events.append({"origin": rec["origin"], "handler": rec["handler"]})
            elif op == "safepoint":
                safepoints.append({"origin": rec["origin"], "roots": rec["roots"]})
            elif op == "halt":
                return {
                    "result": acc,
                    "branch_destinations": branch_destinations,
                    "handler_events": handler_events,
                    "safepoints": safepoints,
                    "step_events": step_events,
                    "sample_events": list(step_events),
                    "encoded_size": artifact["encoded_size"],
                }
        if not jumped:
            pc += 1
    return {
        "result": acc,
        "branch_destinations": branch_destinations,
        "handler_events": handler_events,
        "safepoints": safepoints,
        "step_events": step_events,
        "sample_events": list(step_events),
        "encoded_size": artifact["encoded_size"],
    }
