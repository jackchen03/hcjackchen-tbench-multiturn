# Linear hash index on-disk pivot

This task carries one opaque disk-index writer through layout recovery, anti-canonical split behavior, and a final redistribution-order correction.

## Context chain

1. Step 1 recovers the fixed header, page and slot representation, and base bucket addressing.
2. Step 2 preserves that byte layout while adding chain-triggered splits and newest-first overflow pages.
3. Step 3 retains those behaviors but overrides redistribution with insertion-sequence order and records the decisive probe.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain validation proves reference correctness and guarded boundaries only; it is not model calibration.

