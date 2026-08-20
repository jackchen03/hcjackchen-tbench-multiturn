# Item embeddings garbage-resolution pivot

Repair a truncated primary shard from replica back-pointers, correct cross-shard centering and validate it, then pivot the recovered vectors into a flat true-vector store.

## Context chain

1. Restore structural length and CRC by locating missing IDs in replica back-pointer tables.
2. Preserve the repair while converting replica-centered rows into the primary shard's mean domain.
3. Consolidate true vectors into a flat store and remove all old sharded artifacts.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local proof covers the supplied reference chain and immediate boundaries only. Model calibration remains unmeasured.
