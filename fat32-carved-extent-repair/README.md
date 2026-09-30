# FAT32 carved extent repair

Three context-following steps repair a divergent FAT32 allocation table, recover two deleted SQLite files (including a fragmented file and a damaged start-cluster high word), and close the chain with filesystem, row-count, and hash verification.

## Carried state

- Step 1 creates `fat_decision.txt`, `repaired.img`, and reusable `repair.sh`.
- Step 2 mutates `repaired.img` by restoring directory entries and creates `files_manifest.json` plus reusable `carve.sh`.
- Step 3 consumes the restored image and manifest and creates `outcome.txt` plus reusable `verify.sh`.

## Calibration

| Evaluator | Step 1 | Step 2 | Step 3 | Whole chain |
| --- | --- | --- | --- | --- |
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Other models | unmeasured | unmeasured | unmeasured | unmeasured |

Difficulty remains `pending_phase2` until trajectory evidence exists.
