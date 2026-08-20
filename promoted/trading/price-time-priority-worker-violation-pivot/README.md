# Price-time priority worker violation pivot

This task carries one gateway through single-level arrival ordering, deterministic global ordering, and an overriding sequential-ingress simplification.

## Context chain

1. Step 1 fixes maker order for a single symbol and price while retaining a worker-pool path.
2. Step 2 applies ingress order globally across symbols and prices and makes repeated output byte-identical.
3. Step 3 removes the pool and timestamp ordering in favor of direct sequential ingress.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and over-execution boundaries. Calibration and cloud validation remain unmeasured.
