#!/usr/bin/env python3
"""Independent exact-grader control replay for final audit."""

import datetime
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


TASK = Path(__file__).resolve().parents[1]
IMAGE = "tbench-mt-postgres-cast-stats-partition-pivot:validate"
FINGERPRINT = "bundle-sha256-v1:34237c502d83eca6f0cb200ac342385e2bf33df6fd3f60829ec0ab51aefcf800"
OUT = TASK / ".validation/final-audit-controls-v1.json"
LOGS = TASK / ".validation/final-audit-control-logs"
CASES = [
    ("s1_expression", "1_fix_slow_query", "ACCEPT", "expr_index_cast_kept"),
    ("s1_composite", "1_fix_slow_query", "ACCEPT", "typestable_composite_cust_created"),
    ("s1_cast_plain_mutant", "1_fix_slow_query", "REJECT", "index_only_cast_kept"),
    ("s1_rewrite_no_index", "1_fix_slow_query", "REJECT", "rewrite_no_index"),
    ("s1_settings_only", "1_fix_slow_query", "REJECT", "settings_only"),
    ("s1_bloat", "1_fix_slow_query", "REJECT", "table_bloat"),
    ("s1_hardcode_mutant", "1_fix_slow_query", "REJECT", "id_hardcoding"),
    ("s2_cluster", "2_harden_query", "ACCEPT", "cluster_by_cust_vacuum"),
    ("s2_plain_mutant", "2_harden_query", "REJECT", "plain_index_skew"),
    ("s2_vacuum_only", "2_harden_query", "REJECT", "plain_plus_vacuum"),
    ("s2_partial_only", "2_harden_query", "REJECT", "partial_alone"),
    ("s2_partial_plain", "2_harden_query", "REJECT", "partial_plus_plain"),
    ("s3_monthly", "3_partition_pivot", "ACCEPT", "monthly_hot_layout_variant"),
    ("s3_retune_mutant", "3_partition_pivot", "REJECT", "retune_no_partition"),
    ("s3_btree_mutant", "3_partition_pivot", "REJECT", "hot_btree"),
    ("s1_compatible_early_cluster", "1_fix_slow_query", "ACCEPT", "compatible_s2_superset_on_s1"),
    ("s2_compatible_early_partition", "2_harden_query", "ACCEPT", "compatible_s3_superset_on_s2"),
]
SOURCE_CASE = {
    "s1_compatible_early_cluster": "s2_cluster",
    "s2_compatible_early_partition": "s3_monthly",
}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run(argv, check=False):
    return subprocess.run(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=check,
    )


def junit(container):
    raw = run(["docker", "exec", container, "cat", "/logs/verifier/junit.xml"], check=True).stdout
    root = ET.fromstring(raw)
    suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
    total = sum(int(s.get("tests", 0)) for s in suites)
    failed = sum(int(s.get("failures", 0)) for s in suites)
    errors = sum(int(s.get("errors", 0)) for s in suites)
    skipped = sum(int(s.get("skipped", 0)) for s in suites)
    return {
        "total": total,
        "executed": total - skipped,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
    }


def clean(text):
    return "\n".join(line.rstrip(" \t\r") for line in text.splitlines()) + "\n"


def current_fingerprint():
    helper = Path(
        "/home/hcjackchen/.codex/skills/tbench-task-authoring-multiturn-builder/"
        "scripts/bundle_fingerprint.py"
    )
    output = run(["python3", str(helper), str(TASK)], check=True).stdout
    return next(line for line in output.splitlines() if line.startswith("bundle-sha256-v1:"))


def one(index, item):
    name, step, expected, handoff_id = item
    container = "pg-final-audit-%d-%02d" % (os.getpid(), index)
    verifier_exit = 127
    reward = "missing"
    stats = {"total": 0, "executed": 0, "failed": 0, "errors": 0, "skipped": 0}
    transcript = []
    try:
        started = run(
            [
                "docker", "run", "-d", "--network", "none", "--name", container,
                "--entrypoint", "sleep", IMAGE, "infinity",
            ]
        )
        transcript.append(started.stdout)
        if started.returncode:
            raise RuntimeError("container start failed")
        source_case = SOURCE_CASE.get(name, name)
        copied = run(["docker", "cp", str(TASK / ".validation/controls" / source_case) + "/.", container + ":/app/"])
        transcript.append(copied.stdout)
        if copied.returncode:
            raise RuntimeError("candidate copy failed")
        if step == "3_partition_pivot":
            prep = run(
                ["docker", "exec", container, "sh", "-c", "mkdir -p /app/growth && mv /app/layout.sql /app/growth/layout.sql"]
            )
            transcript.append(prep.stdout)
            if prep.returncode:
                raise RuntimeError("Step-3 layout staging failed")
        prep = run(["docker", "exec", container, "mkdir", "-p", "/tests", "/logs/verifier"])
        copied = run(["docker", "cp", str(TASK / "steps" / step / "tests") + "/.", container + ":/tests/"])
        transcript.extend((prep.stdout, copied.stdout))
        if prep.returncode or copied.returncode:
            raise RuntimeError("grader staging failed")
        graded = run(["docker", "exec", "-w", "/app", container, "bash", "/tests/test.sh"])
        verifier_exit = graded.returncode
        transcript.append(graded.stdout)
        reward = run(["docker", "exec", container, "cat", "/logs/verifier/reward.txt"], check=True).stdout.strip()
        stats = junit(container)
    except Exception as exc:
        transcript.append("HARNESS ERROR %s: %s\n" % (type(exc).__name__, exc))
    finally:
        run(["docker", "rm", "-f", container])
    observed = "ACCEPT" if verifier_exit == 0 and reward == "1" else "REJECT"
    matches = (
        observed == expected
        and stats["executed"] > 0
        and stats["skipped"] == 0
        and stats["errors"] == 0
    )
    log_path = LOGS / (name + ".log")
    log_path.write_text(clean("\n".join(transcript)), encoding="utf-8")
    if not matches:
        print(clean("\n".join(transcript)), flush=True)
    result = {
        "case": name,
        "handoff_id": handoff_id,
        "step": step,
        "expected": expected,
        "observed": observed,
        "matches": matches,
        "reward": reward,
        "verifier_exit": verifier_exit,
        "junit": stats,
        "network": "none",
        "fresh_container": True,
        "log": str(log_path.relative_to(TASK)),
    }
    print(
        "CASE %s handoff=%s expected=%s observed=%s executed=%d skipped=%d match=%s"
        % (name, handoff_id, expected, observed, stats["executed"], stats["skipped"], matches),
        flush=True,
    )
    return result


def main():
    started = now()
    fingerprint = current_fingerprint()
    if fingerprint != FINGERPRINT:
        raise SystemExit("included fingerprint changed: " + fingerprint)
    LOGS.mkdir(parents=True, exist_ok=True)
    results = [one(i, item) for i, item in enumerate(CASES, 1)]
    summary = {
        "cases": len(results),
        "accepted": sum(r["observed"] == "ACCEPT" for r in results),
        "rejected": sum(r["observed"] == "REJECT" for r in results),
        "mismatches": sum(not r["matches"] for r in results),
        "skipped": sum(r["junit"]["skipped"] for r in results),
    }
    doc = {
        "schema": "tbench-final-audit-controls-v1",
        "task": TASK.name,
        "started_at": started,
        "ended_at": now(),
        "bundle_fingerprint": FINGERPRINT,
        "image": IMAGE,
        "network": "none",
        "fresh_container_per_case": True,
        "summary": summary,
        "cases": results,
    }
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print("manifest=" + str(OUT), flush=True)
    if summary["mismatches"] or summary["skipped"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
