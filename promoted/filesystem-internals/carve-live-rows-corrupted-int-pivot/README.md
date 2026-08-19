# Carve live rows from corrupted SQLite pivot

Recover the exact live table from a corrupted SQLite image, add a checksum-index database, then pivot the verified rows into an explicit fixed-width binary archive.

## Context chain

1. Reconstruct only the authoritative live-row payload into a normal SQLite database.
2. Preserve those rows while building the SHA-256 checksum table and value index.
3. Preserve verified data while dropping SQLite/varint output for the `LR01` binary format.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local proof covers the reference chain and immediate over-execution boundaries only. Model calibration remains unmeasured.
