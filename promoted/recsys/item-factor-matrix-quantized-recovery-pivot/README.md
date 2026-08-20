# Item-factor matrix quantized recovery pivot

Recover hidden head-item residual corrections, expose their diagnostics, then pivot the decoder to lazy per-item access while preserving compatibility.

## Context chain

1. Correct `load_item_factors` for head and tail items without changing checkpoint data.
2. Preserve reconstruction and expose head flags plus a diagnostic artifact.
3. Preserve both earlier contracts while moving decode logic into `QuantizedItemStore`.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local validation proves the supplied reference chain and immediate boundaries only. Model calibration remains unmeasured.
