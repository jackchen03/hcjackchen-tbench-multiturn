#!/usr/bin/env python3
"""Run the V9 Phase-1 control inventory through the shipped step graders."""

import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


TASK = Path(__file__).resolve().parents[1]
ARCHIVE = Path(
    "/home/hcjackchen/tbench-authoring-archives/phase2-v9-four-20260930/"
    "gzip-reproducible-layer-pivot"
)
HANDOFF = ARCHIVE / ".meta/handoff.json"
MATRIX = ARCHIVE / "evidence/matrix_v8.py"
SKILL = Path("/home/hcjackchen/.codex/skills/tbench-task-authoring-multiturn-builder")
IMAGE = "tbench-mt-gzip-reproducible-layer-pivot:validate"
EXPECTED_FINGERPRINT = (
    "bundle-sha256-v1:2aa10d734985b7e3bd8c9540e0525c4188d60923d5e98e2b4d7eefa0c0471e67"
)
LOGS = TASK / ".validation/control-logs"
MANIFEST = TASK / ".validation/exact-grader-controls-v1.json"


S1_MUTANTS = {
    "plain_targz": "STARTER_SH",
    "gzip_n_only": "GZIPN_ONLY_SH",
    "clamp_no_manifest": "CLAMP_NO_MANIFEST_SH",
    "legacy_space_manifest": "LEGACY_MANIFEST_SH",
    "wrong_file_payload": "PAYLOAD_FLIP_SH",
    "wrong_member_kind": "KIND_FLIP_SH",
    "wrong_symlink_target": "LINK_TARGET_FLIP_SH",
    "source_mutation_matching_archive": "SOURCE_MUT_SH",
    "uncompressed_tar_named_tgz": "UNCOMPRESSED_SH",
    "starter_noop": None,
    "duplicate_member_exact_spelling": "DUPLICATE_MEMBER_SH",
    "duplicate_member_dot_slash_alias": "DUPLICATE_ALIAS_SH",
}
S2_MUTANTS = {
    "name_sorted_layer": "NAME_SORTED_LAYER_SH",
    "gzipped_layer": "GZIPPED_LAYER_SH",
    "src_recomputed_layer": "SRC_RECOMPUTED_LAYER_SH",
    "manifest_mutation_matching_layer": "MANIFEST_MUT_SH",
    "nonnumeric_owner_metadata": "NONNUMERIC_LAYER_SH",
    "targz_unchanged": None,
}
VALID = [
    (1, "gnu_tar_clamp_chain", "GNU_ALT_SH"),
    (1, "python_tarfile_impl", "TARFILE_ALT_SH"),
    (2, "gnu_tar_explicit_order_layer", "GNU_LAYER_ALT_SH"),
    (2, "python_tarfile_hash_order_layer", "TARFILE_LAYER_ALT_SH"),
]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def invoke(argv, check=False):
    return subprocess.run(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=check,
    )


def normalized(text):
    return "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def extract_candidate_constants():
    """Evaluate only constant string concatenation/replacement assignments."""
    tree = ast.parse(MATRIX.read_text(encoding="utf-8"), filename=str(MATRIX))
    values = {}

    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name) and node.id in values:
            return values[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return evaluate(node.left) + evaluate(node.right)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "replace"
            and not node.keywords
        ):
            base = evaluate(node.func.value)
            args = [evaluate(arg) for arg in node.args]
            return base.replace(*args)
        raise ValueError(ast.dump(node, include_attributes=False))

    wanted = set(x for x in S1_MUTANTS.values() if x)
    wanted.update(x for x in S2_MUTANTS.values() if x)
    wanted.update(x[2] for x in VALID)
    wanted.add("GNU_MANIFEST_WALK")
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            values[target.id] = evaluate(node.value)
        except (KeyError, TypeError, ValueError):
            continue
    missing = sorted(wanted - values.keys())
    if missing:
        raise RuntimeError("could not extract Phase-1 candidate constants: " + repr(missing))
    return values


def bundle_fingerprint():
    proc = invoke(
        ["python3", str(SKILL / "scripts/bundle_fingerprint.py"), str(TASK)],
        check=True,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("bundle-sha256-v1:"):
            return line.strip()
    raise RuntimeError("bundle fingerprint missing from helper output")


def junit_stats(container):
    raw = invoke(
        ["docker", "exec", container, "cat", "/logs/verifier/junit.xml"], check=True
    ).stdout
    root = ET.fromstring(raw)
    suites = [root] if root.tag == "testsuite" else list(root)
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


def grader(container, tests_path):
    run = invoke(
        ["docker", "exec", "-w", "/app", container, "bash", tests_path + "/test.sh"]
    )
    reward = invoke(
        ["docker", "exec", container, "cat", "/logs/verifier/reward.txt"], check=True
    ).stdout.strip()
    stats = junit_stats(container)
    return run, reward, stats


def install_script(container, host_script, destination):
    copied = invoke(["docker", "cp", str(host_script), container + ":" + destination])
    if copied.returncode != 0:
        return copied
    return invoke(["docker", "exec", container, "chmod", "0755", destination])


def copy_tree(container, source, destination):
    made = invoke(["docker", "exec", container, "mkdir", "-p", destination])
    if made.returncode:
        return made
    return invoke(["docker", "cp", str(source) + "/.", container + ":" + destination])


def readonly_mount_probe():
    container = "gzipctrl-isolation-%d" % os.getpid()
    log_parts = []
    start = invoke(
        [
            "docker", "run", "-d", "--network", "none", "--name", container,
            "-v", str(TASK / "steps/1_fix_reproducibility/tests") + ":/tests:ro",
            IMAGE, "sleep", "infinity",
        ]
    )
    log_parts.append("$ docker run --network none -v tests:/tests:ro ...\n" + start.stdout)
    try:
        verdict = invoke(["docker", "exec", "-w", "/app", container, "bash", "/tests/test.sh"])
        log_parts.append("$ /tests/test.sh\n" + verdict.stdout)
        passed = (
            verdict.returncode != 0
            and "Read-only file system" in verdict.stdout
            and "ERROR collecting" in verdict.stdout
        )
    finally:
        removed = invoke(["docker", "rm", "-f", container])
        log_parts.append("$ docker rm -f\n" + removed.stdout)
    log_path = LOGS / "readonly-mount-fail-closed.log"
    log_path.write_text(normalized("\n".join(log_parts)), encoding="utf-8")
    return {
        "case_id": "readonly-mount-fail-closed",
        "expected": "FAIL_BEFORE_CANDIDATE",
        "observed": "FAIL_BEFORE_CANDIDATE" if passed else "ISOLATION_FAILURE",
        "matches": passed,
        "network": "none",
        "log": str(log_path.relative_to(TASK)),
    }


def adapt_to_final_contract(case_id, content):
    """Keep Phase-1 mechanisms while applying the final directory digest rule."""
    if case_id not in {"gnu_tar_clamp_chain", "python_tarfile_impl"}:
        return content, None
    matches = [
        old
        for old in (
            'recs.append(("dir", rel, ""))',
            'acc.append((rel, "dir", ""))',
        )
        if old in content
    ]
    if len(matches) != 1 or content.count(matches[0]) != 1:
        raise RuntimeError("expected one Phase-1 directory digest expression")
    old = matches[0]
    new = old.replace('""))', 'hashlib.sha256(b"").hexdigest()))')
    return (
        content.replace(old, new),
        "directory payload digest changed from an empty string to sha256(empty), "
        "as required by the final manifest contract",
    )


def stage_s1(container):
    parts = []
    prep = invoke(["docker", "exec", container, "mkdir", "-p", "/solution1"])
    parts.append("$ mkdir /solution1\n" + prep.stdout)
    copied = invoke(
        [
            "docker",
            "cp",
            str(TASK / "steps/1_fix_reproducibility/solution") + "/.",
            container + ":/solution1",
        ]
    )
    parts.append("$ copy Step-1 oracle\n" + copied.stdout)
    solved = invoke(["docker", "exec", "-w", "/app", container, "bash", "/solution1/solve.sh"])
    parts.append("$ /solution1/solve.sh\n" + solved.stdout)
    if prep.returncode or copied.returncode or solved.returncode:
        raise RuntimeError("Step-1 staging failed\n" + "\n".join(parts))
    tested, reward, stats = grader(container, "/tests1")
    parts.append("$ /tests1/test.sh\n" + tested.stdout)
    if tested.returncode or reward != "1" or stats["skipped"] or stats["executed"] < 1:
        raise RuntimeError("Step-1 staging grader failed\n" + "\n".join(parts))
    cleared = invoke(
        ["docker", "exec", container, "sh", "-c", "rm -rf /solution1 /logs/verifier"]
    )
    if cleared.returncode:
        raise RuntimeError("could not clear Step-1 staging verifier output")
    return parts, stats


def run_case(index, spec, scripts, candidate_dir):
    step = spec["step"]
    case_id = spec["case_id"]
    container = "gzipctrl-%d-%02d" % (os.getpid(), index)
    log_parts = []
    candidate_name = spec["constant"]
    candidate_sha = None
    candidate_source = None
    candidate_adaptation = None
    setup_exit = 0
    stage_stats = None
    verifier_exit = 127
    reward = "missing"
    stats = {"total": 0, "executed": 0, "failed": 0, "errors": 0, "skipped": 0}
    try:
        start = invoke(
            [
                "docker",
                "run",
                "-d",
                "--network",
                "none",
                "--name",
                container,
                IMAGE,
                "sleep",
                "infinity",
            ]
        )
        log_parts.append("$ docker run --network none ...\n" + start.stdout)
        if start.returncode:
            raise RuntimeError("container start failed")
        copied_tests1 = copy_tree(
            container, TASK / "steps/1_fix_reproducibility/tests", "/tests1"
        )
        copied_tests2 = copy_tree(container, TASK / "steps/2_layer_pivot/tests", "/tests2")
        log_parts.append(
            "$ docker cp private test trees\n" + copied_tests1.stdout + copied_tests2.stdout
        )
        if copied_tests1.returncode or copied_tests2.returncode:
            raise RuntimeError("could not copy private verifier trees")

        if step == 2:
            staged, stage_stats = stage_s1(container)
            log_parts.extend(staged)

        if candidate_name is None:
            if step == 1:
                starter = TASK / "environment/starter_pack.sh"
                candidate_source = str(starter)
                candidate_sha = sha256_bytes(starter.read_bytes())
                log_parts.append("$ retain image starter /app/pack.sh\n")
            else:
                candidate_source = "absent /app/make_layer.sh"
                log_parts.append("$ retain Step-1-only state; do not install make_layer.sh\n")
        else:
            content, candidate_adaptation = adapt_to_final_contract(
                case_id, scripts[candidate_name]
            )
            candidate = candidate_dir / (case_id + ".sh")
            candidate.write_text(content, encoding="utf-8")
            candidate_sha = sha256_bytes(content.encode("utf-8"))
            candidate_source = str(MATRIX) + ":" + candidate_name
            destination = "/app/pack.sh" if step == 1 else "/app/make_layer.sh"
            installed = install_script(container, candidate, destination)
            log_parts.append("$ install %s\n%s" % (candidate_name, installed.stdout))
            if installed.returncode:
                setup_exit = installed.returncode

        if step == 2 and candidate_name is not None and setup_exit == 0:
            setup = invoke(
                [
                    "docker",
                    "exec",
                    "-w",
                    "/app",
                    container,
                    "/app/make_layer.sh",
                    "/app/src",
                    "/app/manifest.jsonl",
                    "/app/layer.tar",
                ]
            )
            setup_exit = setup.returncode
            log_parts.append("$ public make_layer interface\n" + setup.stdout)

        test_path = "/tests1" if step == 1 else "/tests2"
        tested, reward, stats = grader(container, test_path)
        verifier_exit = tested.returncode
        log_parts.append("$ %s/test.sh\n%s" % (test_path, tested.stdout))
    except Exception as exc:
        log_parts.append("HARNESS ERROR: %s: %s\n" % (type(exc).__name__, exc))
    finally:
        removed = invoke(["docker", "rm", "-f", container])
        log_parts.append("$ docker rm -f\n" + removed.stdout)

    observed = "ACCEPT" if verifier_exit == 0 and reward == "1" else "REJECT"
    clean_junit = stats["skipped"] == 0 and stats["executed"] >= 1
    matches = observed == spec["expected"] and clean_junit
    log_path = LOGS / (case_id + ".log")
    log_path.write_text(normalized("\n".join(log_parts)), encoding="utf-8")
    return {
        "case_id": case_id,
        "step": step,
        "role": spec["role"],
        "expected": spec["expected"],
        "observed": observed,
        "matches": matches,
        "candidate_constant": candidate_name,
        "candidate_source": candidate_source,
        "candidate_adaptation": candidate_adaptation,
        "candidate_sha256": candidate_sha,
        "setup_exit": setup_exit,
        "verifier_exit": verifier_exit,
        "reward": reward,
        "junit": stats,
        "step1_stage_junit": stage_stats,
        "network": "none",
        "fresh_container": True,
        "log": str(log_path.relative_to(TASK)),
    }


def main():
    started = now()
    fingerprint = bundle_fingerprint()
    if fingerprint != EXPECTED_FINGERPRINT:
        raise SystemExit("included fingerprint changed: " + fingerprint)

    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    phase1_s1 = handoff["failureAttribution"]["1"]["mutants"]
    phase1_s2 = handoff["failureAttribution"]["2"]["mutants"]
    if phase1_s1 != list(S1_MUTANTS) or phase1_s2 != list(S2_MUTANTS):
        raise SystemExit("runner inventory differs from V9 failureAttribution")
    if handoff["overExecMap"] != {"1": [], "2": []}:
        raise SystemExit("unexpected applicable over-execution boundary")

    expected_valid = handoff["validAlternativeControls"]
    if expected_valid != {
        "1": ["gnu_tar_clamp_chain", "python_tarfile_impl"],
        "2": ["gnu_tar_explicit_order_layer", "python_tarfile_hash_order_layer"],
    }:
        raise SystemExit("runner valid controls differ from V9 handoff")

    scripts = extract_candidate_constants()
    specs = []
    specs.extend(
        {"step": 1, "case_id": key, "constant": value, "role": "mutant", "expected": "REJECT"}
        for key, value in S1_MUTANTS.items()
    )
    specs.extend(
        {"step": 2, "case_id": key, "constant": value, "role": "mutant", "expected": "REJECT"}
        for key, value in S2_MUTANTS.items()
    )
    specs.extend(
        {"step": step, "case_id": case_id, "constant": constant, "role": "valid-alternative", "expected": "ACCEPT"}
        for step, case_id, constant in VALID
    )

    LOGS.mkdir(parents=True, exist_ok=True)
    isolation = readonly_mount_probe()
    print(
        "%s expected=%s observed=%s match=%s"
        % (isolation["case_id"], isolation["expected"], isolation["observed"], isolation["matches"]),
        flush=True,
    )
    results = []
    with tempfile.TemporaryDirectory(prefix="gzip-control-candidates-") as temp:
        candidate_dir = Path(temp)
        for index, spec in enumerate(specs, 1):
            result = run_case(index, spec, scripts, candidate_dir)
            results.append(result)
            print(
                "%s expected=%s observed=%s executed=%d skipped=%d match=%s"
                % (
                    result["case_id"],
                    result["expected"],
                    result["observed"],
                    result["junit"]["executed"],
                    result["junit"]["skipped"],
                    result["matches"],
                ),
                flush=True,
            )

    summary = {
        "cases": len(results),
        "expected_accept": sum(r["expected"] == "ACCEPT" for r in results),
        "expected_reject": sum(r["expected"] == "REJECT" for r in results),
        "observed_accept": sum(r["observed"] == "ACCEPT" for r in results),
        "observed_reject": sum(r["observed"] == "REJECT" for r in results),
        "mismatches": sum(not r["matches"] for r in results),
        "skipped": sum(r["junit"]["skipped"] for r in results),
    }
    manifest = {
        "schema": "gzip-exact-grader-controls-v1",
        "task": "gzip-reproducible-layer-pivot",
        "started_at": started,
        "ended_at": now(),
        "bundle_fingerprint": fingerprint,
        "image": IMAGE,
        "network": "none",
        "test_delivery": "docker-cp writable private directories",
        "isolation_probe": isolation,
        "fresh_container_per_case": True,
        "phase1_inventory_source": str(HANDOFF) + ":failureAttribution",
        "phase1_mutant_inventory": {"1": phase1_s1, "2": phase1_s2},
        "phase1_valid_alternatives": expected_valid,
        "over_execution": {
            "applicable_boundaries": handoff["overExecMap"],
            "status": "NOT_REQUIRED",
        },
        "preserved_prior_evidence": [
            ".validation/control-matrix.log",
            ".validation/run-mutant-controls.sh",
        ],
        "summary": summary,
        "cases": results,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("manifest=" + str(MANIFEST))
    if summary["mismatches"] or summary["skipped"] or not isolation["matches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
