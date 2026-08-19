# Incremental SfM chamfer drift pivot

This task repairs coupled track-uniqueness and parallax-gating defects, adds a run-derived quality report, then pivots both track membership and export format.

## Context chain

1. Step 1 removes duplicate-image track poison and restores far well-conditioned points while retaining NPZ export.
2. Step 2 preserves the reconstruction and derives report counts from each actual run.
3. Step 3 preserves geometry/reporting while replacing the old helper with hash-based component overlap and replacing NPZ with binary PLY.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves reference behavior and guarded transitions only; calibration remains unmeasured.
