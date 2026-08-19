# Stateful escape segment framer pivot

The task carries one byte-exact storage dialect through context-sensitive escaping and then overrides its remainder handling with a mandatory empty final block.

## Context chain

1. Step 1 recovers magic markers, 16-byte blocks, Fletcher footers, and remainder encoding for the basic slice.
2. Step 2 preserves that framing while extending the escape look-ahead to a null successor.
3. Step 3 preserves both clauses but always emits the final block, including an empty one at exact boundaries.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
