# slab-tombstone-coalesce-rebuild

Three context-following turns recover a deliberately noncanonical 4 KiB slab-page compaction dialect.

- Step 1 records every byte-difference run, the measured free-gap length, and absolute input slot geometry.
- Step 2 reuses that ORIGIN geometry to predict probed tail entries while localizing death-order slot sorting and lower-address coalescing.
- Step 3 implements a self-contained rebuild and is graded on disjoint pages with the probe reference unavailable.

The report verifiers validate contract-fixed structure and values derived from the solver-visible pages. Step 2 accepts normalized semantic variants rather than a single source spelling. The final verifier derives expected pages independently and rejects public-output hardcoding and delegation to exact, renamed, wrapped, or lightly modified copies of the solve-time reference.

The revised Phase-1 wording permits canonical proof: the fresh local chain is red before each step and green after the cumulative oracle with zero skips, and both compatible-additive boundaries are recorded `NOT_REQUIRED`. The shipped image runs as the real unprivileged `app` user.

## Calibration

| Actor | Step 1 | Step 2, reached | Step 3, reached | Whole chain |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |

Difficulty hypotheses remain `pending_phase2` until external trajectory evidence exists.
