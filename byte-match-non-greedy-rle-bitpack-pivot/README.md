# Byte-match non-greedy RLE bit-pack pivot

This task carries one executable encoder through a functional hybrid page, byte-identical legacy recovery, and an overriding dictionary-only format.

## Context chain

1. Step 1 establishes the `C0` container, stdin/stdout interface, and decodable RUN/literal framing.
2. Step 2 preserves that interface while replacing greedy choices with the legacy global byte-minimizing dialect.
3. Step 3 retains the header, even-width rule, and tail packing but removes RLE and pivots to first-appearance dictionary indices.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain validation proves reference correctness and guarded boundaries only; it is not model calibration.
