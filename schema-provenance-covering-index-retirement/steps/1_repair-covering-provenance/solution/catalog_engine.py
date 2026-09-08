"""Projection-correct implementation; retirement remains deliberately conservative."""
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

def execute(scenario):
    reads, witnesses, steps = _reads(scenario)
    nodes = sorted(scenario.get("nodes", []))
    roots = sorted(set(scenario.get("current_roots", [])))
    return {"reads": reads, "diagnostics": {"witnesses": witnesses, "projection_steps": steps, "heap_fallbacks": 0, "reindexes": 0}, "retirement": {"retained": nodes, "roots": [{"id": r, "authority": "current"} for r in roots], "paths": [], "maintenance_steps": len(nodes)}}
