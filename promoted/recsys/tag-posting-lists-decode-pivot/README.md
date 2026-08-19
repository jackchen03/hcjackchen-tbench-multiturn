# Tag posting lists decode pivot

This three-step task carries a reverse-engineered posting-list format through a skip-aware point lookup, then overrides the legacy mixed-base decoder for a fixed unified encoding.

## Context chain

1. Step 1 recovers full and headerless trailing blocks while respecting dictionary frequency.
2. Step 2 reuses the discovered layout to jump by skip metadata without decoding preceding blocks, while retaining the decoder.
3. Step 3 keeps the legacy decoder and lookup intact but adds a separate decoder whose blocks all start with absolute IDs.

The chain is non-decorative: the lookup requires the legacy tail semantics learned in step 1, and the final pivot must deliberately discard those semantics only for the new index while preserving both old artifacts.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence under `.validation/` proves only the reference path and boundary probes. It does not measure model completion or calibration.
