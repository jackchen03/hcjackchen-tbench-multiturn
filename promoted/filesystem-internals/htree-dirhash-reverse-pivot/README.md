# Htree dirhash reverse pivot

This task carries one noncanonical ext4-style directory hash through ASCII recovery, high-bit signedness correction, and an overriding bulk-placement interface.

## Context chain

1. Step 1 reproduces major and minor hash words for ASCII filenames across varying seeds and lengths.
2. Step 2 preserves the recovered premix while splitting signed and unsigned byte handling for high-bit names.
3. Step 3 replaces both single-file workflows with one raw-byte bulk interface and deterministic JSON buckets.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local validation proves only the reference chain and immediate successor boundaries. Oracle ×3, model calibration, and cloud validation remain unmeasured.
