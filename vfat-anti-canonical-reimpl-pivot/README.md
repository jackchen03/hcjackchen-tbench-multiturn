# VFAT anti-canonical reimplementation pivot

This task carries one directory-entry generator through byte-exact recovery of a quirky dialect, long-name listing, and an overriding canonical VFAT representation with cluster manifests.

## Context chain

1. Step 1 reproduces global tail numbering, always-LFN output, NTRes zeroing, and the extra terminator slot.
2. Step 2 parses that exact carried format back into the original UTF-8 insertion order.
3. Step 3 removes the quirky formatter and implements per-basis tails, canonical slot counts, 8.3 case optimization, and contiguous cluster assignments.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence proves only the reference path and immediate over-execution boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
