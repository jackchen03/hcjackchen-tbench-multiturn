#!/usr/bin/env python3
"""Run Phase-1 alternatives and mutants through the shipped per-step graders."""

import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess


TASK = Path(__file__).resolve().parents[1]
VALIDATION = TASK / ".validation"
CONTROLS = VALIDATION / "controls"
LOGS = VALIDATION / "control-logs"
IMAGE = "tbench-mt-ffmpeg-downmix-loudnorm-pivot:validate"
ARCHIVE = Path(
    "/home/hcjackchen/tbench-authoring-archives/phase2-v9-four-20260930/"
    "ffmpeg-downmix-loudnorm-pivot"
)
FINGERPRINT_TOOL = Path(
    "/home/hcjackchen/.codex/skills/tbench-task-authoring-multiturn-builder/"
    "scripts/bundle_fingerprint.py"
)


CASES = [
    {
        "id": "s1-valid-volume-highpass-pan",
        "step": 1,
        "role": "valid-alternative",
        "expected": "ACCEPT",
        "script": CONTROLS / "s1-volume-chain.sh",
    },
    {
        "id": "s1-valid-staging-corner-variant",
        "step": 1,
        "role": "valid-alternative",
        "expected": "ACCEPT",
        "script": CONTROLS / "s1-corner-variant.sh",
    },
    {
        "id": "s1-valid-awk-dsp-linear",
        "step": 1,
        "role": "valid-alternative",
        "expected": "ACCEPT",
        "script": ARCHIVE / "evidence/awkdsp_impl.sh",
    },
    {
        "id": "s1-compatible-early-loudnorm",
        "step": 1,
        "role": "over-exec-compatible-positive",
        "expected": "ACCEPT",
        "script": CONTROLS / "s1-compatible-early-loudnorm.sh",
    },
    {
        "id": "s1-mutant-naive-oneliner",
        "step": 1,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s1-naive.sh",
    },
    {
        "id": "s1-mutant-starter-noop",
        "step": 1,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s1-naive.sh",
    },
    {
        "id": "s1-mutant-clip-first",
        "step": 1,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s1-clip-first.sh",
    },
    {
        "id": "s1-mutant-no-dc-blocker",
        "step": 1,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s1-no-dc-blocker.sh",
    },
    {
        "id": "s1-mutant-limiter-only",
        "step": 1,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s1-limiter-only.sh",
    },
    {
        "id": "s1-mutant-public-path-hardcode",
        "step": 1,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s1-public-path-hardcode.sh",
    },
    {
        "id": "s2-valid-single-pass-loudnorm",
        "step": 2,
        "role": "valid-alternative",
        "expected": "ACCEPT",
        "script": CONTROLS / "s2-single-pass.sh",
    },
    {
        "id": "s2-valid-dual-pass-loudnorm",
        "step": 2,
        "role": "valid-alternative",
        "expected": "ACCEPT",
        "script": CONTROLS / "s2-dual-pass.sh",
    },
    {
        "id": "s2-mutant-peak-only",
        "step": 2,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s2-peak-only.sh",
    },
    {
        "id": "s2-mutant-tag-only",
        "step": 2,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s2-tag-only.sh",
    },
    {
        "id": "s2-mutant-s1-unchanged",
        "step": 2,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s2-unchanged.sh",
    },
    {
        "id": "s2-mutant-no-48k-resample",
        "step": 2,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s2-no-resample.sh",
    },
    {
        "id": "s2-mutant-public-path-hardcode",
        "step": 2,
        "role": "mutant",
        "expected": "REJECT",
        "script": CONTROLS / "s2-public-path-hardcode.sh",
    },
]


def invoke(argv, check=False):
    return subprocess.run(
        [str(x) for x in argv],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=check,
    )


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_script(container, source):
    result = invoke(["docker", "cp", source, "%s:/app/downmix.sh" % container])
    if result.returncode:
        return result
    return invoke(["docker", "exec", container, "chmod", "755", "/app/downmix.sh"])


def exec_in(container, argv):
    return invoke(["docker", "exec", container] + list(argv))


def copy_tree(container, source, destination):
    made = exec_in(container, ["mkdir", "-p", destination])
    if made.returncode:
        return made
    return invoke(["docker", "cp", str(source) + "/.", "%s:%s" % (container, destination)])


def readonly_mount_probe():
    name = "ffctrl-isolation-%d" % os.getpid()
    log_parts = []
    start = invoke(
        [
            "docker", "run", "-d", "--network", "none", "--name", name,
            "-v", "%s:/tests:ro" % (TASK / "steps/1_fix_downmix/tests"),
            IMAGE, "sleep", "infinity",
        ]
    )
    log_parts.append("$ docker run --network none -v tests:/tests:ro ...\n" + start.stdout)
    try:
        verdict = exec_in(name, ["bash", "/tests/test.sh"])
        log_parts.append("$ /tests/test.sh\n" + verdict.stdout)
        passed = (
            verdict.returncode != 0
            and "Read-only file system" in verdict.stdout
            and "ERROR collecting" in verdict.stdout
        )
    finally:
        removed = invoke(["docker", "rm", "-f", name])
        log_parts.append("$ docker rm -f\n" + removed.stdout)
    log_path = LOGS / "readonly-mount-fail-closed.log"
    log_path.write_text("\n".join(line.rstrip(" \t") for line in "\n".join(log_parts).splitlines()) + "\n")
    return {
        "case_id": "readonly-mount-fail-closed",
        "expected": "FAIL_BEFORE_CANDIDATE",
        "observed": "FAIL_BEFORE_CANDIDATE" if passed else "ISOLATION_FAILURE",
        "matches": passed,
        "network": "none",
        "log": str(log_path.relative_to(TASK)),
    }


def run_case(case, index):
    name = "ffctrl-%d-%02d" % (os.getpid(), index)
    log_parts = []
    start = invoke(
        ["docker", "run", "-d", "--network", "none", "--name", name,
         IMAGE, "sleep", "infinity"]
    )
    log_parts.append("$ docker run ...\n" + start.stdout)
    setup_exit = None
    verifier_exit = None
    try:
        if start.returncode:
            observed = "HARNESS_ERROR"
        else:
            copied_tests1 = copy_tree(name, TASK / "steps/1_fix_downmix/tests", "/tests1")
            copied_tests2 = copy_tree(name, TASK / "steps/2_loudnorm_pivot/tests", "/tests2")
            copied_solution1 = copy_tree(name, TASK / "steps/1_fix_downmix/solution", "/solution1")
            log_parts.append("$ docker cp private test/solution trees\n" + copied_tests1.stdout + copied_tests2.stdout + copied_solution1.stdout)
            if copied_tests1.returncode or copied_tests2.returncode or copied_solution1.returncode:
                raise RuntimeError("could not copy private verifier/solution trees")
            if case["step"] == 2:
                prefix = exec_in(name, ["bash", "/solution1/solve.sh"])
                log_parts.append("$ /solution1/solve.sh\n" + prefix.stdout)
                if prefix.returncode == 0:
                    prefix_test = exec_in(name, ["bash", "/tests1/test.sh"])
                    log_parts.append("$ /tests1/test.sh\n" + prefix_test.stdout)
                else:
                    prefix_test = prefix
                if prefix.returncode or prefix_test.returncode:
                    observed = "HARNESS_ERROR"
                else:
                    copied = copy_script(name, case["script"])
                    log_parts.append("$ install control\n" + copied.stdout)
                    first = exec_in(
                        name,
                        ["/app/downmix.sh", "/app/mix.wav", "/app/mixA.wav"],
                    )
                    second = exec_in(
                        name,
                        ["/app/downmix.sh", "/app/episodeB.wav", "/app/mixB.wav"],
                    )
                    setup_exit = max(copied.returncode, first.returncode, second.returncode)
                    log_parts.append("$ public pair setup\n" + first.stdout + second.stdout)
                    verdict = exec_in(name, ["bash", "/tests2/test.sh"])
                    verifier_exit = verdict.returncode
                    log_parts.append("$ /tests2/test.sh\n" + verdict.stdout)
                    observed = "ACCEPT" if verifier_exit == 0 else "REJECT"
            else:
                copied = copy_script(name, case["script"])
                log_parts.append("$ install control\n" + copied.stdout)
                setup = exec_in(
                    name,
                    ["/app/downmix.sh", "/app/source.wav", "/app/mix.wav"],
                )
                setup_exit = max(copied.returncode, setup.returncode)
                log_parts.append("$ public output setup\n" + setup.stdout)
                verdict = exec_in(name, ["bash", "/tests1/test.sh"])
                verifier_exit = verdict.returncode
                log_parts.append("$ /tests1/test.sh\n" + verdict.stdout)
                observed = "ACCEPT" if verifier_exit == 0 else "REJECT"
    finally:
        removed = invoke(["docker", "rm", "-f", name])
        log_parts.append("$ docker rm -f\n" + removed.stdout)

    log_path = LOGS / (case["id"] + ".log")
    log_text = "\n".join(log_parts)
    log_path.write_text("\n".join(line.rstrip(" \t") for line in log_text.splitlines()) + "\n")
    return {
        "case_id": case["id"],
        "step": case["step"],
        "role": case["role"],
        "expected": case["expected"],
        "observed": observed,
        "matches": observed == case["expected"],
        "setup_exit": setup_exit,
        "verifier_exit": verifier_exit,
        "script": str(case["script"]),
        "script_sha256": file_sha(case["script"]),
        "log": str(log_path.relative_to(TASK)),
    }


def main():
    LOGS.mkdir(parents=True, exist_ok=True)
    fingerprint_out = invoke(["python3", FINGERPRINT_TOOL, TASK], check=True).stdout
    fingerprint = next(
        line.strip() for line in fingerprint_out.splitlines() if line.startswith("bundle-sha256-v1:")
    )
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    isolation = readonly_mount_probe()
    print(
        "%s expected=%s observed=%s match=%s"
        % (isolation["case_id"], isolation["expected"], isolation["observed"], isolation["matches"]),
        flush=True,
    )
    results = []
    for index, case in enumerate(CASES, 1):
        result = run_case(case, index)
        results.append(result)
        print(
            "%s expected=%s observed=%s match=%s"
            % (result["case_id"], result["expected"], result["observed"], result["matches"]),
            flush=True,
        )
    manifest = {
        "schema": "ffmpeg-exact-grader-controls-v1",
        "task": TASK.name,
        "bundle_fingerprint": fingerprint,
        "image": IMAGE,
        "network": "none",
        "test_delivery": "docker-cp writable private directories",
        "isolation_probe": isolation,
        "started_at": started,
        "ended_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cases": results,
        "summary": {
            "cases": len(results),
            "expected_accept": sum(r["expected"] == "ACCEPT" for r in results),
            "expected_reject": sum(r["expected"] == "REJECT" for r in results),
            "observed_accept": sum(r["observed"] == "ACCEPT" for r in results),
            "observed_reject": sum(r["observed"] == "REJECT" for r in results),
            "mismatches": sum(not r["matches"] for r in results),
        },
        "over_execution": {
            "boundary": "1_fix_downmix->2_loudnorm_pivot",
            "status": "NOT_REQUIRED",
            "reason": "Step 1 does not forbid compatible loudness processing",
            "positive_case": "s1-compatible-early-loudnorm",
        },
    }
    path = VALIDATION / "exact-grader-controls-v1.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("manifest=%s" % path)
    return 1 if manifest["summary"]["mismatches"] or not isolation["matches"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
