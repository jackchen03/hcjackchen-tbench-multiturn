# ICP registrar adaptive-rejection pivot

The task carries one point-cloud registrar through exact reproduction of a legacy biased trace, an additive overlap report, and an overriding pivot back to unbiased geometric alignment.

## Context chain

1. Step 1 matches the opaque registrar's adaptive pose and verbose trajectory.
2. Step 2 preserves that pose behavior and writes report fields from the actual final trace row.
3. Step 3 removes the legacy bias and report, producing fixed-policy geometric registration.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
