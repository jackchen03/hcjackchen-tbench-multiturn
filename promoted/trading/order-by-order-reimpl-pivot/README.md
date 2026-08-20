# Order-by-order book reimplementation pivot

This task carries one order-book rebuilder through recovery of a legacy exchange dialect, instrumentation of its unusual branches, and an overriding pivot to canonical semantics.

## Context chain

1. Step 1 reproduces the opaque legacy binary's zero-retention and replace-priority behavior.
2. Step 2 preserves that byte-exact snapshot contract while adding `/app/quirks_report.json`.
3. Step 3 overrides both legacy quirks: executions remove zero-size orders, every replace moves to the tail, and the pivot writes `/app/3_pivot_to_canonical_report.json`.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
