# Committed table-state savepoint pivot

This task recovers a custom one-shot unwind dialect, applies it incrementally to the exact recovered map, then overrides it with retention and abort-on-miss semantics.

## Context chain

1. Step 1 reconstructs committed state using the opaque v1 adjudication and global survivor order.
2. Step 2 preserves v1 semantics while applying an incremental log atop the exact text shape produced previously.
3. Step 3 stages the v2 evidence and replaces consumption/no-op resolution with retention/abort behavior.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain validation proves reference correctness and guarded boundaries only; it is not model calibration.

