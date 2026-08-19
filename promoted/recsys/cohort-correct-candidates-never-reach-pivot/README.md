# Cohort-correct candidates ranking pivot

This task carries one recommendation pipeline through item-id normalization, cohort-aware metrics, and an overriding hierarchy-based category-affinity assembly.

## Context chain

1. Step 1 canonicalizes padded backfill IDs before the item feature lookup, restoring backfill recall without changing the frozen ranker.
2. Step 2 measures backfill and category cohorts from the carried recommendations using the hierarchy to identify category-sensitive gold items.
3. Step 3 changes ranking assembly to roll leaf categories to top categories before affinity lookup, restoring both cohorts.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
