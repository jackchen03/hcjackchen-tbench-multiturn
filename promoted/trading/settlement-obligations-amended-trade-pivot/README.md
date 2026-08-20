# Settlement obligations amended-trade pivot

The task carries terminal FX trade state and the custodian spot-date convention through a funding extension, then overrides the net-only reporting model with separate gross pay and receive exposure.

## Context chain

1. Step 1 repairs terminal AMEND/CANCEL collapse and the distinct USD final-date gate.
2. Step 2 consumes the corrected settlement CSV and aggregates funding across counterparties without reimplementing netting.
3. Step 3 retains terminal-state and spot-date behavior while replacing net-only aggregation with gross exposure and deprecating the old output.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
