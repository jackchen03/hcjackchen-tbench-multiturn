# Crash-recovery replay pivot

The task carries one recovered WAL replay dialect through cumulative auditing, then overrides its anti-canonical mutations with engine-v2 semantics.

## Context chain

1. Step 1 reproduces XOR delta, conditional prune, and bespoke same-LSN ordering.
2. Step 2 preserves those bytes while reporting applied-record and prune counts.
3. Step 3 preserves pageLSN filtering but replaces the quirks with overwrite, unconditional prune, and stream order.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
