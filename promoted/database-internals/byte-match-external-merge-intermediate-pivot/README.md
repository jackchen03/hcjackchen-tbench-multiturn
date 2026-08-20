# Byte-match external merge intermediate pivot

This task carries one external-sort implementation through basic correctness, exact recovery of a noncanonical spill dialect, and an overriding heap-based merge pivot that preserves every intermediate file.

## Context chain

1. Step 1 builds `/app/polysort`, emitting sorted output and valid run containers.
2. Step 2 preserves that interface while matching the reference output and every spill byte-for-byte across cascading merge passes.
3. Step 3 replaces the merge selection core with `heapq`, retains the recovered spill semantics, and keeps all intermediate runs for downstream inspection.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
