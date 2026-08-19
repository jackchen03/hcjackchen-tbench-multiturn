# Committed snapshot data-pages pivot

This task carries authoritative transaction-state decoding through committed-snapshot reconstruction, then overrides the text-report path with direct binary page repair.

## Context chain

1. Step 1 ignores the misleading page hint and diagnoses top versions whose transactions are not committed.
2. Step 2 reuses that decoding to walk undo chains until a committed predecessor is found, omitting aborted insert origins.
3. Step 3 preserves the reconstruction logic but writes a clean, sorted binary page file with null undo pointers and committed metadata.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain validation proves reference correctness and guarded boundaries only; it is not model calibration.

