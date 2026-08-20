# Exchange pro-rata allocation dialect pivot

The task carries one matcher through recovery of a top-order carve-out dialect, iterative minimum-fill repooling, and an overriding fairness pivot that removes the carve-out while retaining repooling and adding participant aggregation.

## Context chain

1. Step 1 recovers the old residual-capacity carve-out allocation.
2. Step 2 retains that allocation and adds iterative MIN_FILL repooling.
3. Step 3 removes the old carve-out, retains MIN_FILL behavior, changes the fractional tie-break, and emits the PnL impact report.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
