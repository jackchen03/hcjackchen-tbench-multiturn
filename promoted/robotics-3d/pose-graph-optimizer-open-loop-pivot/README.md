# Pose-graph optimizer open-loop pivot

The task carries a single SE(2) optimizer through per-edge direction reconciliation and full anisotropic weighting, then overrides the batch trajectory format for live SLAM consumption.

## Context chain

1. Step 1 preserves forward odometry while correcting reversed loop measurements.
2. Step 2 retains that direction handling and replaces diagonal weighting with the full covariance inverse.
3. Step 3 preserves the MLE but switches to input node order, continuous angles, and a loop-correction report.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate boundary probes. Model calibration remains unmeasured.
