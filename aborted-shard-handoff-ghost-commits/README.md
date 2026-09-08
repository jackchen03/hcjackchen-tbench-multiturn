# Aborted shard handoff ghost commits

This two-step task carries the solver's repaired Go simulator and its ticket/journal model into an abort-and-recovery extension. Step 1 establishes full admission identity and separate effect/reply durability across a live handoff. Step 2 adds crash recovery, stale-control fencing, two-sided reconciliation, and final-owner certificate-gated collection without replacing the earlier behavior. The transition is state-dependent and additive; a compatible Step-2 superset is valid at Step 1, so the 1→2 over-execution probe is `NOT_REQUIRED`.

## Completion calibration

| Agent | Step 1 | Step 2 | Whole task |
| --- | --- | --- | --- |
| Oracle | 3/3 (1.0) | 3/3 (1.0) | 3/3 (1.0) |
| Avocado | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured |

Oracle rows report the local reference-stability run for this exact bundle. Model difficulty remains unmeasured until external trials exist.
