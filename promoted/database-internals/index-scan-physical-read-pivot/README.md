# Index-scan physical read pivot

This task carries one scattered B+ tree range scan through demand-order recovery, textbook adaptive prefetch, and an overriding residency/extent dialect.

## Context chain

1. Step 1 parses the fixture, descends the tree, and emits demand reads in sibling-chain order while suppressing resident pages.
2. Step 2 adds a bounded doubling readahead window with physical-adjacency resets and demand/prefetch interleaving.
3. Step 3 changes residency from a free skip to a consumed budget position and clamps batches at physical extent boundaries.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local validation proves only the reference chain and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
