# Stale page valid checksum double-write pivot

The chain separates checksum eligibility from currency, carries committed-LSN recovery into a latest heap rebuild, and then pivots to target-batch PITR with a page-by-page provenance manifest.

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

