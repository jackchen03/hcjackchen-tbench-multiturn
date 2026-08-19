# Recycled WAL committed-set pivot

Recover the true committed set before a recycled WAL generation boundary, build its byte-exact sorted commit index, then pivot that sidecar to a deterministic chained hash format.

## Context chain

1. Stop replay on block-address or per-record predecessor-chain discontinuity.
2. Preserve recovery while writing `CIDX` entries with exact commit LSNs.
3. Preserve the text set and LSN map while replacing `CIDX` with the 64-bucket `CIDY` index.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local proof covers the supplied reference chain and immediate boundaries only. Model calibration remains unmeasured.
