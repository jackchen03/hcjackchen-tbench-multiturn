# Already-served item set recovery pivot

This task carries one recovered bitmap codec through exact reading, canonical round-trip writing, and an overriding streaming iterator plus sort-merge audit path.

## Context chain

1. Step 1 recovers ARRAY delta-varints, big-endian BITMAP words, inclusive RUN containers, directory flags, and CRC validation.
2. Step 2 preserves the reader, adds canonical type selection and writing, and exposes a compatibility iterator.
3. Step 3 replaces set-backed iteration with mmap-backed per-container streaming and audits sorted candidates without materializing the served set.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
