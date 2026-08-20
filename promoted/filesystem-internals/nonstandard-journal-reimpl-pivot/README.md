# Nonstandard journal reimplementation pivot

This task carries one opaque anti-canonical block-journal dialect through replay and auditing, then replaces it with canonical recovery behavior.

## Context chain

1. Step 1 differentially recovers the nonstandard replay decisions and writes exact block images.
2. Step 2 reuses the same parser and checksum decisions to audit commits, revokes, and escaped blocks.
3. Step 3 drops those quirks and implements the canonical checksum, tag geometry, revoke boundary, and escape magic.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain validation proves reference correctness and guarded transitions only; it is not model calibration.
