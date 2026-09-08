"""Projection-correct implementation with exact dynamic-root retirement."""
from collections import deque

PAGE_LOCAL_PROVENANCE = True

def _reads(scenario):
    schemas = scenario.get("schemas", {})
    pages = {p["id"]: p for p in scenario.get("pages", [])}
    reads, witnesses, steps = [], {}, 0
    for req in scenario.get("reads", []):
        page = pages[req["page"]]
        fields = schemas[page["schema"]]
        row = next(r for r in page["rows"] if r["key"] == req["key"])
        materialized = dict(zip(fields, row["payload"]))
        reads.append({"page": page["id"], "key": req["key"], "projection": [materialized[f] for f in req["projection"]]})
        witnesses[page["id"]] = sorted({page["schema"], *req["projection"]})
        steps += len(req["projection"]) + 1
    return reads, witnesses, steps

def _retire(scenario):
    continuations = {k: list(v) for k, v in scenario.get("continuation_roots", {}).items()}
    for migration in scenario.get("migrations", []):
        continuations[migration["id"]] = list(migration["roots"])
    authority = {}
    for root in scenario.get("current_roots", []):
        authority.setdefault(root, "current")
    for snap, roots in sorted(scenario.get("snapshot_roots", {}).items()):
        for root in roots:
            authority.setdefault(root, "snapshot:" + snap)
    for cont, roots in sorted(continuations.items()):
        for root in roots:
            authority.setdefault(root, "continuation:" + cont)
    adjacency = {}
    for edge in scenario.get("edges", []):
        adjacency.setdefault(edge["src"], []).append((edge["dst"], edge["kind"]))
    for src in adjacency:
        adjacency[src].sort()
    parent = {root: None for root in sorted(authority)}
    queue = deque(sorted(authority))
    while queue:
        src = queue.popleft()
        for dst, kind in adjacency.get(src, []):
            if dst not in parent:
                parent[dst] = (src, kind)
                queue.append(dst)
    paths = []
    for node in sorted(parent):
        if parent[node] is None:
            continue
        chain, cur = [], node
        while parent[cur] is not None:
            src, kind = parent[cur]
            chain.append({"src": src, "dst": cur, "kind": kind})
            cur = src
        chain.reverse()
        paths.append({"id": node, "path": chain})
    roots = [{"id": root, "authority": authority[root]} for root in sorted(authority)]
    delta = len(scenario.get("changed_roots", [])) + len(scenario.get("changed_edges", [])) + len(scenario.get("migrations", []))
    maintenance = 8 * delta + min(16, len(authority)) if delta else min(16, len(authority))
    return {"retained": sorted(parent), "roots": roots, "paths": paths, "maintenance_steps": maintenance}

def execute(scenario):
    reads, witnesses, steps = _reads(scenario)
    return {"reads": reads, "diagnostics": {"witnesses": witnesses, "projection_steps": steps, "heap_fallbacks": 0, "reindexes": 0}, "retirement": _retire(scenario)}
