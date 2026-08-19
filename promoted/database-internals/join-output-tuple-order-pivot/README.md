# Join output tuple-order pivot

Recover a deterministic anti-canonical hash-join output order, add build-byte-triggered recursion, then pivot recursed partitions to recursive child-grouped emission.

## Context chain

1. Match fit partitions using spill-completion ordering and probe-major emission.
2. Preserve fit behavior while adding one level of byte-threshold child partitioning and a report.
3. Generalize child grouping recursively and remove the flat recursed-partition path.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local proof covers the supplied reference chain and immediate boundaries only; model calibration remains unmeasured.
