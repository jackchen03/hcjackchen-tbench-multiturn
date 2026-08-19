# Restored MF checkpoint held-out pivot

The task carries one recovered matrix-factorization checkpoint through diagnosis of completion-order drift, then overrides the flat NumPy serving format with an mmap-compatible bundle.

## Context chain

1. Step 1 joins physical checkpoint rows to WAL identities and selects the highest training step.
2. Step 2 preserves those factors and reports exactly where last file position would select stale state.
3. Step 3 preserves the drift report but replaces and removes the flat factor files with a contiguous serving mmap.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
