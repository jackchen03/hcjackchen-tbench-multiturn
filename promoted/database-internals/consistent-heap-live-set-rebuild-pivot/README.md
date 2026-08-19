# Consistent heap live-set rebuild pivot

The task carries canonical MVCC visibility through an FSM rebuild, then overrides page-only visibility with a signed residual witness for unstamped deletes.

## Context chain

1. Step 1 resolves xmin/xmax against the durable commit log.
2. Step 2 preserves that live set and rebuilds free-space bytes from tuple lengths.
3. Step 3 preserves abort handling but uses only positive FSM residuals to localize one hidden delete.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
