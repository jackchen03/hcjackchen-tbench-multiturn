#!/usr/bin/env python3
"""Build INDEX.md (usable-tasks table) + REJECTED.md from a bulk MULTI-TURN T-Bench discovery run.

Usage:
    python3 build_catalog.py <workflow_output_file> [outDir]

<workflow_output_file> is the Workflow task `.output` file (a JSON wrapper containing a
"result" field) — or any file holding the raw result JSON. outDir defaults to the result's
own outDir.

INDEX.md is intentionally minimal: a single "## Usable tasks" table with columns
# | family | dynamic | steps | title | conf | dir. No provenance line, no counts, no rejected
section. `dir` is the task's REAL folder, derived from the written instruction.md path (the
model-reported slug can differ from the folder it wrote to). `steps` is the step count and
`dynamic` is context-following / context-overriding / both. Rejected candidates and their reasons
go to REJECTED.md so the index stays clean.
"""
import json, os, sys


def load_result(path):
    obj = json.load(open(path, encoding="utf-8"))
    data = obj.get("result", obj) if isinstance(obj, dict) else obj
    if isinstance(data, str):
        data = json.loads(data)
    return data


def real_dir(t, outdir):
    """The actual folder on disk for this task — trust the written path over the slug."""
    p = t.get("instruction_path") or t.get("dossier_path") or ""
    d = os.path.basename(os.path.dirname(p)) if p else ""
    if d and os.path.isdir(os.path.join(outdir, d)):
        return d
    slug = t.get("slug") or t.get("dir") or ""
    if slug and os.path.isdir(os.path.join(outdir, slug)):
        return slug
    return slug or d or "task"


def proof_status(outdir, d, n_steps=0):
    vdir = os.path.join(outdir, d, ".validation")
    if not os.path.isdir(vdir):
        return "unproven"
    runs = sorted(f for f in os.listdir(vdir) if f.startswith("chain-") and f.endswith(".json"))
    if not runs:
        return "unproven"
    try:
        with open(os.path.join(vdir, runs[-1]), encoding="utf-8") as fh:
            res = json.load(fh)
    except (OSError, ValueError):
        return "unproven"
    phases = res.get("phases") or []
    if not phases:
        return "unproven"
    if res.get("failures"):
        return "chain FAIL"
    if res.get("unproven") or any(p.get("status") != "OK" for p in phases):
        return "chain PARTIAL"
    graded = {p.get("step") for p in phases if p.get("phase") == "GREEN" and p.get("status") == "OK"}
    if n_steps and len(graded) < n_steps:
        return "chain PARTIAL"
    return "chain PASS"


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: build_catalog.py <workflow_output_file> [outDir]")
    data = load_result(sys.argv[1])
    tasks = data.get("tasks", [])
    rejected = data.get("rejected", [])
    gate_blocked = data.get("gateBlocked", [])
    outdir = sys.argv[2] if len(sys.argv) > 2 else data.get("outDir", ".")
    os.makedirs(outdir, exist_ok=True)

    seed_name = os.path.basename(str(data.get("seed", data.get("repo", ""))).rstrip("/")) or "T-Bench"
    ordered = sorted(tasks, key=lambda x: (x.get("family", ""), -float(x.get("confidence", 0))))

    L = [f"# {seed_name} multi-turn terminal-bench task catalog\n\n",
         "`proof` is what the oracle chain actually did in Docker, not an opinion. `unproven` "
         "means `run_oracle_chain.py` has not been run on that task yet — those tasks are drafts, "
         "not validated tasks.\n\n## Usable tasks\n\n",
         "| # | family | dynamic | steps | title | conf | proof | dir |\n"
         "|---|---|---|---|---|---|---|---|\n"]
    counts = {"chain PASS": 0, "chain PARTIAL": 0, "chain FAIL": 0, "unproven": 0}
    for i, t in enumerate(ordered, 1):
        n_steps = t.get("n_steps") or len(t.get("steps", []) or [])
        d = real_dir(t, outdir)
        proof = proof_status(outdir, d, n_steps)
        counts[proof] = counts.get(proof, 0) + 1
        L.append("| {} | {} | {} | {} | {} | {:.2f} | {} | `{}/` |\n".format(
            i, t.get("family", ""), t.get("dynamic", ""), n_steps, t.get("title", ""),
            float(t.get("confidence", 0)), proof, d))
    open(os.path.join(outdir, "INDEX.md"), "w", encoding="utf-8").writelines(L)

    R = [f"# {seed_name} — rejected candidates\n\n"]
    for r in rejected:
        R.append("## {} ({})\n\n{}\n\n".format(
            r.get("title", "?"), r.get("family", "?"), r.get("reason", "")))
    if gate_blocked:
        R.append("# Authored but blocked by the static gate\n\n")
        for g in gate_blocked:
            R.append("## {}\n\nremaining: {}\n\nfixes applied: {}\n\n".format(
                g.get("slug", "?"), ", ".join(g.get("remaining_codes", []) or ["?"]),
                g.get("fixed_summary", "")))
    open(os.path.join(outdir, "REJECTED.md"), "w", encoding="utf-8").writelines(R)

    print("Wrote {} ({} usable: {} chain PASS, {} chain PARTIAL, {} chain FAIL, {} unproven) and "
          "REJECTED.md ({} rejected, {} gate-blocked)".format(
              os.path.join(outdir, "INDEX.md"), len(ordered), counts.get("chain PASS", 0),
              counts.get("chain PARTIAL", 0), counts.get("chain FAIL", 0), counts.get("unproven", 0),
              len(rejected), len(gate_blocked)))


if __name__ == "__main__":
    main()
