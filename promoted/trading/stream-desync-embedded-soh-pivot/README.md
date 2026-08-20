# FIX stream desynchronization pivot

This task carries one gateway through RawData framing, dictionary-driven handling of the full length-prefixed field family, and an overriding checksum/resynchronization stage with dropped-frame reporting.

## Context chain

1. Step 1 preserves embedded SOH bytes inside RawData.
2. Step 2 retains that framing and reads all Length-to-Data pairs from the exchange dictionary.
3. Step 3 retains the family parser, validates CheckSum, resynchronizes after corrupt frames, and writes the drop report.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only reference behavior and boundary probes. Model calibration remains unmeasured.
