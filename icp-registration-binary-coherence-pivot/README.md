# ICP registration binary coherence pivot

This task carries one ICP implementation through partial-overlap trimming, outlier-aware correspondence gating, and an overriding indexed-search performance pivot.

## Context chain

1. Step 1 restores the reference basin on clean and partial-overlap scans while retaining brute-force correspondence search.
2. Step 2 preserves that trim behavior and extends correspondence handling for incompatible-normal outlier clusters.
3. Step 3 preserves all earlier poses while replacing brute-force correspondence search with deterministic `cKDTree` lookup.

The chain is non-decorative because each later step mutates the same registration implementation and is regression-graded against all earlier pair families.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves reference behavior and boundary enforcement only; model calibration remains unmeasured.
