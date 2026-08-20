# MoldUDP64 gap detection multi-message pivot

This task carries one offline reconciler through global sequence accounting, sentinel handling, and overlapping retransmit deduplication.

## Context chain

1. Step 1 fixes global sequence accounting for packets carrying several messages.
2. Step 2 preserves that accounting while excluding heartbeat and end-of-session sentinels.
3. Step 3 replaces packet-start deduplication with first-wins per-message sequence storage.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.

