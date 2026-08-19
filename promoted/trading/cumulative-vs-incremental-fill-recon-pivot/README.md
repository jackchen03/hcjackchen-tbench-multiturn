# Cumulative versus incremental fill reconciliation pivot

This task carries one FIX drop-copy reconciler through correct cumulative-to-incremental reconstruction, a detailed ordered fill ledger, and an overriding LastQty-only gross-exposure implementation with hash-indexed deduplication.

## Context chain

1. Step 1 handles carry and reset replace acknowledgements, omitted LastQty, and PossDup records while preserving flat net output.
2. Step 2 reuses the same true-fill stream to emit a transitive-root audit ledger in appearance order.
3. Step 3 removes cumulative quantity entirely, switches dedup to a tuple-keyed dictionary, and changes output to buy/sell/gross/net objects.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
