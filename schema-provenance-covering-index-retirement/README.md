# Schema provenance covering-index retirement

This two-step task carries the repaired Python catalog engine, its persisted page witnesses, and the live alias/snapshot/continuation graph into metadata retirement. Step 1 makes covering reads use page-local projection provenance. Step 2 computes exact post-migration dependency closure and certificates while preserving those carried reads. It removes unreachable metadata but does not override the Step-1 contract.

## Completion calibration

| Agent | Step 1 | Step 2 | Whole task |
| --- | --- | --- | --- |
| Oracle | 3/3 (1.0) | 3/3 (1.0) | 3/3 (1.0) |
| Avocado | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured |

Oracle rows report the local reference-stability run for this exact bundle. Model difficulty remains unmeasured until external trials exist.
