# Word-aligned bitmap index anti-canonical pivot

This task carries a byte-exact opaque bitmap dialect through direct point lookup, then overrides the compressed representation with a simpler raw format.

## Context chain

1. Step 1 reverse-engineers the legacy byte layout and creates `/app/indexer`.
2. Step 2 preserves those exact bytes while adding `/app/query`, which must parse the persisted index directly.
3. Step 3 follows newly staged migration evidence, replaces the writer with the v2 raw representation, and removes the query and legacy codec logic.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and guarded transition boundaries; it is not model calibration.

