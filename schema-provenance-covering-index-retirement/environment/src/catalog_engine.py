"""Runnable starter with projection-alias and conservative-retirement defects."""

PAGE_LOCAL_PROVENANCE = False

def _resolve(schema, aliases):
    seen = set()
    while schema in aliases and schema not in seen:
        seen.add(schema)
        schema = aliases[schema]
    return schema

def execute(scenario):
    schemas = scenario.get("schemas", {})
    aliases = {a["src"]: a["dst"] for a in scenario.get("aliases", [])}
    pages = {p["id"]: p for p in scenario.get("pages", [])}
    reads, witnesses, steps = [], {}, 0
    for req in scenario.get("reads", []):
        page = pages[req["page"]]
        source_schema = _resolve(page["schema"], aliases)
        fields = schemas[source_schema]
        row = next(r for r in page["rows"] if r["key"] == req["key"])
        materialized = dict(zip(fields, row["payload"]))
        reads.append({"page": page["id"], "key": req["key"], "projection": [materialized.get(f) for f in req["projection"]]})
        witnesses[page["id"]] = sorted({source_schema, *req["projection"]})
        steps += len(req["projection"]) + 1
    nodes = sorted(scenario.get("nodes", []))
    roots = sorted(set(scenario.get("current_roots", [])))
    return {"reads": reads, "diagnostics": {"witnesses": witnesses, "projection_steps": steps, "heap_fallbacks": 0, "reindexes": 0}, "retirement": {"retained": nodes, "roots": [{"id": r, "authority": "current"} for r in roots], "paths": [], "maintenance_steps": len(nodes)}}
