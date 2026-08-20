# Two-regime undistortion asymmetric-radius pivot

This multi-turn task carries one Python undistorter through discovery of a radius-dependent truncated regime, its radial warm start, and a final mixed-domain tangential pivot.

## Context chain

1. Preserve the converged inner inverse while reproducing the reference's identity-initialized single outer step.
2. Replace the outer identity initialization with the asymmetric radial warm start, retaining the prior branch.
3. Pivot only the outer tangential radius slots to distorted-domain `rd2`, retaining both earlier fixes.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain validation proves the supplied reference path and the immediate over-execution boundaries only. Model calibration remains unmeasured.
