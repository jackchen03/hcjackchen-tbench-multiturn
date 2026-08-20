# Byte-exact mixed insert/delete pages

This three-turn task carries one executable and its generated state forward. Each turn adds or deliberately replaces a storage-engine rule; the final turn tests the requested pivot as well as representative earlier behavior that remains applicable.

## Completion rates

| Solver | Step 1 | Step 2 | Step 3 | Whole chain |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |

Local Docker chain proof is recorded separately under `.validation/` and is not model calibration.

