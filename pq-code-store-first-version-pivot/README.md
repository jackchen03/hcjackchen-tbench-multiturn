# PQ code-store first-version pivot

This task carries one custom PQ serializer through decoder recovery, a byte-identical writer, and an overriding resilience change for broken offset tables and CRC enforcement.

## Context chain

1. Step 1 repairs keyframe/delta decoding while leaving later reports and random access absent.
2. Step 2 reuses the recovered mask/XOR semantics to add the canonical writer and its report.
3. Step 3 overrides the trusted-offset assumption, rebuilds boundaries from variable records, enforces CRC, and adds targeted random access.

The chain is non-decorative: the writer must reproduce the decoder’s recovered byte semantics exactly, while the last step must remove an assumption that was valid for the original samples.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only reference correctness and guarded boundaries, not model calibration.
