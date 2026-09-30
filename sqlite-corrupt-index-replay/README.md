# SQLite corrupt-index recovery and replay

This two-step task begins with a committed WAL tail and a corrupted partial index. The first turn must recover the database without sacrificing committed rows, produce a strict recovery report, and repair the crash-safety configuration. The second turn carries that exact repaired database forward and replaces the starter append-only replay with max-sequence, retry-safe behavior while preserving every repaired invariant.

## Context chain

1. `1_recover_index` creates a family-general recovery interface and repairs the planted database, report, and configuration.
2. `2_idempotent_replay` uses the actual Step-1 database and configuration, mutates the table according to the replay input, and reasserts the complete Step-1 contract.

The transition is compatible-additive: Step 1 does not forbid an already hardened replay implementation, so over-execution is `NOT_REQUIRED`. Under-execution remains observable because the carried starter replay fails on correction records.

## Completion measurements

| Runner | Step 1 | Step 2 | Whole task |
|---|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured |

Local chain proof, model calibration, novelty, contamination, and cloud validation are recorded separately and must not be inferred from this table.
