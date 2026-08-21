# Formatter clusters metadata pivot

This task carries one deterministic filesystem formatter through recovery of its STRIDE=1 flex-clustered layout, absolute stride alignment with used-pad accounting, and a final flex-index modulo pivot for inode-table placement.

## Context chain

1. Step 1 reproduces byte-exact STRIDE=1 images, including the superblock, GDT, clustered metadata, root inode, and root directory.
2. Step 2 preserves that layout while aligning all three metadata segments and accounting for zero-filled padding as used blocks.
3. Step 3 retains the earlier behavior and adds the non-zero `F mod STRIDE` inode-table bump for later flexes.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
