#!/usr/bin/env python3
import json
import sys

sys.path.insert(0, "/app/src")
from catalog_engine import execute

def main():
    for line in sys.stdin:
        try:
            scenario = json.loads(line)
            print(json.dumps(execute(scenario), sort_keys=True, separators=(",", ":")))
        except Exception:
            print('{"error":"invalid_scenario"}')
            return 1
    return 0

raise SystemExit(main())
