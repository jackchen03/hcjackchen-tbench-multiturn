#!/usr/bin/env python3
"""Run Phase-2 alternatives and mutants through the shipped step graders."""

import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


TASK = Path(__file__).resolve().parents[1]
IMAGE = "tbench-mt-sqlite-corrupt-index-replay:controls"
CANARY = "6ed650ac-e37a-43df-b61c-6e07b1a7be30"
FINGERPRINT_TOOL = Path(
    "/home/hcjackchen/.codex/skills/tbench-task-authoring-multiturn-builder/"
    "scripts/bundle_fingerprint.py"
)


def run(argv, *, input_text=None, timeout=300, check=True):
    result = subprocess.run(
        argv,
        input=input_text,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(argv)}\n"
            f"{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
        )
    return result


def install_text(container, path, text):
    run(
        ["docker", "exec", "-i", container, "sh", "-c", f"cat > {path} && chmod 755 {path}"],
        input_text=text,
    )


def parse_junit(raw):
    root = ET.fromstring(raw)
    suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
    cases = []
    for suite in suites:
        for case in suite.findall("testcase"):
            failed = case.find("failure") is not None or case.find("error") is not None
            skipped = case.find("skipped") is not None
            cases.append({"name": case.get("name"), "passed": not failed and not skipped})
    return cases


RECOVER_COMMON = r'''
baseline = None
for line in open('/app/checker.log'):
    if line.startswith('durable_rows='):
        baseline = int(line.split('=', 1)[1])
count = db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
db.close()
REPORT
CONF
'''


def recover_candidate(mode, report="normal", config=True):
    if mode == "noop":
        return "#!/bin/sh\nexit 0\n"
    setup = ""
    if mode == "wal_delete":
        setup = "import os\nfor s in ('-wal','-shm'):\n    try: os.remove(path+s)\n    except FileNotFoundError: pass\n"
    elif mode == "adversarial":
        setup = (
            "import os\n"
            "probe={}\n"
            "def denied(name, action):\n"
            " try:\n"
            "  action(); probe[name]='ALLOWED'\n"
            " except OSError as exc:\n"
            "  probe[name]='denied:'+type(exc).__name__\n"
            "denied('tests',lambda: open('/tests/test_outputs.py','rb').read(1))\n"
            "denied('seal_list',lambda: os.listdir('/tmp/codimango/sqlite-corrupt-index-replay-s1'))\n"
            "parent=os.getppid()\n"
            "try:\n"
            " status=open('/proc/%d/status'%parent).read().splitlines()\n"
            " grand=int(next(x.split()[1] for x in status if x.startswith('PPid:')))\n"
            "except OSError:\n"
            " grand=1\n"
            "denied('harness_mem',lambda: open('/proc/%d/mem'%grand,'rb').read(1))\n"
            "denied('harness_fds',lambda: os.listdir('/proc/%d/fd'%grand))\n"
            "open('/app/isolation_probe.json','w').write(json.dumps(probe,sort_keys=True))\n"
            "if any(value=='ALLOWED' for value in probe.values()): raise SystemExit(91)\n"
        )
    operation = "db.execute('REINDEX idx_big')\n"
    if mode == "dump":
        operation = (
            "dump = '\\n'.join(db.iterdump())\n"
            "db.close()\n"
            "import os\n"
            "for s in ('','-wal','-shm'):\n"
            "    try: os.remove(path+s)\n"
            "    except FileNotFoundError: pass\n"
            "db = sqlite3.connect(path, isolation_level=None)\n"
            "db.executescript(dump)\n"
        )
    elif mode == "vacuum":
        operation = (
            "import os\n"
            "vac = path + '.vacuum'\n"
            "try: os.remove(vac)\n"
            "except FileNotFoundError: pass\n"
            "db.execute(\"VACUUM INTO '%s'\" % vac.replace(\"'\", \"''\"))\n"
            "db.close()\n"
            "for s in ('','-wal','-shm'):\n"
            "    try: os.remove(path+s)\n"
            "    except FileNotFoundError: pass\n"
            "os.replace(vac, path)\n"
            "db = sqlite3.connect(path, isolation_level=None)\n"
            "db.execute('REINDEX idx_big')\n"
        )
    checkpoint = "" if mode == "no_checkpoint" else "db.execute('PRAGMA wal_checkpoint(TRUNCATE)')\n"
    hardcode = ""
    if mode == "hardcode":
        hardcode = (
            "db.execute(\"DELETE FROM orders WHERE order_id NOT LIKE 's007-%'\")\n"
            "db.execute('PRAGMA wal_checkpoint(TRUNCATE)')\n"
        )
    if report == "string":
        report_code = "json.dump({'rows_recovered': str(count-baseline), 'method': 'repair'}, open('/app/recovery_report.json','w'))"
    elif report == "bool":
        report_code = "json.dump({'rows_recovered': True, 'method': 'repair'}, open('/app/recovery_report.json','w'))"
    elif report == "extra":
        report_code = "json.dump({'rows_recovered': count-baseline, 'method': 'repair', 'debug': 1}, open('/app/recovery_report.json','w'))"
    else:
        report_code = "json.dump({'rows_recovered': count-baseline, 'method': 'repair'}, open('/app/recovery_report.json','w'))"
    conf_code = (
        "open('/app/app.conf','w').write('synchronous=NORMAL\\nwal_autocheckpoint=1000\\n')"
        if config
        else "pass"
    )
    body = RECOVER_COMMON.replace("REPORT", report_code).replace("CONF", conf_code)
    return (
        "#!/bin/sh\nset -eu\nDB=${1:?}\npython3 - \"$DB\" <<'PY'\n"
        "import json, sqlite3, sys\npath=sys.argv[1]\n"
        + setup
        + "db=sqlite3.connect(path,isolation_level=None)\n"
        + operation
        + checkpoint
        + "db.execute('PRAGMA wal_autocheckpoint=1000')\n"
        + hardcode
        + body
        + "PY\n"
    )


REPLAY_ARGV = (
    "inp=sys.argv[1] if len(sys.argv)>1 else '/app/orders_input.jsonl'\n"
    "path=sys.argv[2] if len(sys.argv)>2 else '/app/store.db'\n"
)


REPLAY_CANDIDATES = {
    "s2-valid-upsert": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\n"
        + "with db:\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw)\n"
        + "  db.execute('INSERT INTO orders VALUES(?,?,?,?) ON CONFLICT(order_id) DO UPDATE SET seq=excluded.seq,amount=excluded.amount,status=excluded.status WHERE excluded.seq>orders.seq',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + "db.close()\n"
    ),
    "s2-valid-guard-update": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\n"
        + "with db:\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw); old=db.execute('SELECT seq FROM orders WHERE order_id=?',(r['order_id'],)).fetchone()\n"
        + "  if old is None: db.execute('INSERT INTO orders VALUES(?,?,?,?)',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + "  elif r['seq']>old[0]: db.execute('UPDATE orders SET seq=?,amount=?,status=? WHERE order_id=?',(r['seq'],r['amount'],r['status'],r['order_id']))\n"
        + "db.close()\n"
    ),
    "s2-valid-staging-merge": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\n"
        + "with db:\n"
        + " db.execute('CREATE TEMP TABLE staged(order_id TEXT,seq INTEGER,amount REAL,status TEXT)')\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw); db.execute('INSERT INTO staged VALUES(?,?,?,?)',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + " db.execute('INSERT INTO orders SELECT order_id,seq,amount,status FROM (SELECT *,ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY seq DESC) n FROM staged) WHERE n=1 ON CONFLICT(order_id) DO UPDATE SET seq=excluded.seq,amount=excluded.amount,status=excluded.status WHERE excluded.seq>orders.seq')\n"
        + "db.close()\n"
    ),
    "s2-mutant-naive": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path,isolation_level=None)\n"
        + "for raw in open(inp):\n"
        + " r=json.loads(raw); db.execute('INSERT INTO orders VALUES(?,?,?,?)',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
    ),
    "s2-mutant-skip": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\nwith db:\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw)\n"
        + "  if db.execute('SELECT 1 FROM orders WHERE order_id=?',(r['order_id'],)).fetchone() is None: db.execute('INSERT INTO orders VALUES(?,?,?,?)',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + "db.close()\n"
    ),
    "s2-mutant-ignore": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\nwith db:\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw); db.execute('INSERT OR IGNORE INTO orders VALUES(?,?,?,?)',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + "db.close()\n"
    ),
    "s2-mutant-last-write-wins": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\nwith db:\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw); db.execute('INSERT INTO orders VALUES(?,?,?,?) ON CONFLICT(order_id) DO UPDATE SET seq=excluded.seq,amount=excluded.amount,status=excluded.status',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + "db.close()\n"
    ),
    "s2-mutant-hardcode": (
        "import json,sqlite3,sys\n" + REPLAY_ARGV
        + "db=sqlite3.connect(path)\nwith db:\n"
        + " for raw in open(inp):\n"
        + "  r=json.loads(raw)\n"
        + "  if r['order_id'].startswith('s007-'): db.execute('INSERT INTO orders VALUES(?,?,?,?) ON CONFLICT(order_id) DO UPDATE SET seq=excluded.seq,amount=excluded.amount,status=excluded.status WHERE excluded.seq>orders.seq',(r['order_id'],r['seq'],r['amount'],r['status']))\n"
        + "db.close()\n"
    ),
}


S1_CASES = {
    "s1-valid-reindex": (recover_candidate("reindex"), True),
    "s1-valid-dump-restore": (recover_candidate("dump"), True),
    "s1-valid-vacuum": (recover_candidate("vacuum"), True),
    "s1-valid-adversarial-isolation": (recover_candidate("adversarial"), True),
    "s1-mutant-noop": (recover_candidate("noop"), False),
    "s1-mutant-wal-delete": (recover_candidate("wal_delete"), False),
    "s1-mutant-no-config": (recover_candidate("reindex", config=False), False),
    "s1-mutant-no-checkpoint": (recover_candidate("no_checkpoint"), False),
    "s1-mutant-behavioral-hardcode": (recover_candidate("hardcode"), False),
    "s1-mutant-report-string": (recover_candidate("reindex", report="string"), False),
    "s1-mutant-report-bool": (recover_candidate("reindex", report="bool"), False),
    "s1-mutant-report-extra": (recover_candidate("reindex", report="extra"), False),
}


def grade_case(name, step, candidate, expected_accept):
    safe = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
    container = f"tbench-sqlite-control-{safe}-{os.getpid()}"
    run(["docker", "rm", "-f", container], check=False)
    started = run(["docker", "run", "-d", "--name", container, IMAGE, "sleep", "infinity"])
    try:
        if not started.stdout.strip():
            raise RuntimeError("container did not start")
        if step == 1:
            install_text(container, "/app/recover.sh", candidate)
            run(
                ["docker", "exec", container, "sh", "/app/recover.sh", "/app/store.db"],
                check=False,
            )
            test_dir = TASK / "steps/1_recover_index/tests"
        else:
            run(["docker", "exec", container, "mkdir", "-p", "/solution"])
            run(
                [
                    "docker",
                    "cp",
                    f"{TASK / 'steps/1_recover_index/solution'}/.",
                    f"{container}:/solution",
                ]
            )
            run(["docker", "exec", container, "bash", "/solution/solve.sh"])
            run(["docker", "exec", container, "rm", "-rf", "/solution"])
            install_text(container, "/app/replay.py", candidate)
            test_dir = TASK / "steps/2_idempotent_replay/tests"
        run(["docker", "exec", container, "rm", "-rf", "/tests", "/logs/verifier"], check=False)
        run(["docker", "exec", container, "mkdir", "-p", "/tests", "/logs/verifier"])
        run(["docker", "cp", f"{test_dir}/.", f"{container}:/tests"])
        graded = run(["docker", "exec", "-w", "/app", container, "bash", "/tests/test.sh"], check=False)
        reward_result = run(
            ["docker", "exec", container, "cat", "/logs/verifier/reward.txt"], check=False
        )
        junit_result = run(
            ["docker", "exec", container, "cat", "/logs/verifier/junit.xml"], check=False
        )
        reward = reward_result.stdout.strip()
        accepted = graded.returncode == 0 and reward == "1"
        tests = parse_junit(junit_result.stdout) if junit_result.returncode == 0 else []
        isolation_probe = None
        if name == "s1-valid-adversarial-isolation":
            probe_result = run(
                ["docker", "exec", container, "cat", "/app/isolation_probe.json"],
                check=False,
            )
            if probe_result.returncode == 0:
                isolation_probe = json.loads(probe_result.stdout)
        return {
            "name": name,
            "step": step,
            "expected": "ACCEPT" if expected_accept else "REJECT",
            "observed": "ACCEPT" if accepted else "REJECT",
            "matched": accepted == expected_accept,
            "tests": tests,
            "isolation_probe": isolation_probe,
            "stdout_tail": graded.stdout[-1000:],
            "stderr_tail": graded.stderr[-1000:],
        }
    finally:
        run(["docker", "rm", "-f", container], check=False)


def main():
    run(["docker", "build", "-q", "-t", IMAGE, str(TASK / "environment")], timeout=1800)
    results = []
    for name, (candidate, expected) in S1_CASES.items():
        result = grade_case(name, 1, candidate, expected)
        print(name, result["observed"], "matched=" + str(result["matched"]), flush=True)
        results.append(result)
    for name, candidate in REPLAY_CANDIDATES.items():
        expected = name.startswith("s2-valid-")
        result = grade_case(name, 2, candidate, expected)
        print(name, result["observed"], "matched=" + str(result["matched"]), flush=True)
        results.append(result)
    payload = {
        "schema": "sqlite-phase2-controls-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "image": IMAGE,
        "canary": CANARY,
        "bundle_fingerprint": run(
            [sys.executable, str(FINGERPRINT_TOOL), str(TASK)]
        ).stdout.strip(),
        "results": results,
        "summary": {
            "total": len(results),
            "accepted": sum(row["observed"] == "ACCEPT" for row in results),
            "rejected": sum(row["observed"] == "REJECT" for row in results),
            "mismatches": sum(not row["matched"] for row in results),
        },
    }
    out = TASK / ".validation/controls-v1.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], sort_keys=True))
    raise SystemExit(0 if payload["summary"]["mismatches"] == 0 else 1)


if __name__ == "__main__":
    main()
