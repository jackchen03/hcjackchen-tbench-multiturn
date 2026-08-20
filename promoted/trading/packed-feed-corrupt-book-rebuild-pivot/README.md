# Packed feed corrupt book rebuild pivot

The chain first removes phantom alignment from packed records, then recovers mixed-endian field decoding and order-id semantics, and finally pivots to the version-gated v2 AddOrder layout.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain proof is correctness evidence only. Oracle ×3, model calibration, and cloud validation remain unmeasured.

