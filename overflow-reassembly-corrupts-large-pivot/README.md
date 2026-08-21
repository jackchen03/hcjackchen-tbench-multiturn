# Overflow reassembly corrupts large blobs pivot

This task carries one raw-page recovery workflow through inventory, chain-consistent overflow reconstruction, and an overriding content-addressed storage migration.

## Context chain

1. Step 1 scans SQLite-style leaf cells and reports row IDs, declared BLOB sizes, and page size without using SQLite.
2. Step 2 infers the hidden usable-page size from overflow chain consistency and writes byte-exact per-row files through a reusable carver.
3. Step 3 hashes those bytes into a deduplicated store, writes the row manifest, and removes the old row-addressed layout.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
