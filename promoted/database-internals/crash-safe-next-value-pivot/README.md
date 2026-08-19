# Crash-safe next-value pivot

The task carries binary sequence recovery through committed-use auditing, then overrides cached block recovery with a max-committed durable counter.

## Context chain

1. Step 1 folds post-checkpoint reservations into each crash-safe next value.
2. Step 2 preserves those values and adds COMMIT-filtered consumed ids.
3. Step 3 preserves the audit filter but ignores checkpoint/refill state for the new counter scheme.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
