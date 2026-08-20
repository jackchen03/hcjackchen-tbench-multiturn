# Calibrated ranking monotone pivot

This three-step task carries one serving implementation across a calibration-loader repair, a bucket-boundary alignment, and an overriding pivot from the binary calibration path to JSON hot reload with an audit artifact.

## Context chain

1. Step 1 preserves serialized bucket-id provenance while leaving edge-equality behavior unchanged.
2. Step 2 retains the loader repair and aligns serving with the offline right-open bucket convention.
3. Step 3 retains ranking correctness, removes binary parsing, reloads JSON by mtime, and writes the calibration audit.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence, when present under .validation, proves only the reference path and boundary probes. It does not measure model completion or calibration.
