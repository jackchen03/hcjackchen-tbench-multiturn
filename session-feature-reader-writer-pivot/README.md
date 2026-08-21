# Session feature reader/writer scan pivot

The task carries one recovered binary layout through a byte-identical writer, then overrides a full-decode query path with a direct raw-byte containment scan while preserving the codec API.

## Context chain

1. Step 1 recovers the session feature reader from sample shards and decoded sidecars.
2. Step 2 retains that decoder and adds the canonical aligned, checksummed writer.
3. Step 3 preserves both codec functions but pivots item containment to a direct scan that skips event payload decoding.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
