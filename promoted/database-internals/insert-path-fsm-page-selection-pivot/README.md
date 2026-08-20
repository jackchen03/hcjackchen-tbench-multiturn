# Insert-path FSM page-selection pivot

Recover an anti-canonical free-space-map selection dialect, persist the resulting state, then pivot the loader to append-only placement and remove the old FSM path.

## Context chain

1. Match sticky-cursor, ceil-category, retry-and-continue page selection.
2. Preserve landing decisions while writing the caller-provided updated state.
3. Drop FSM selection and state output in favor of last-page-or-extend append-only placement.

## Completion measurements

| Runner | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| Oracle | 3/3 | 3/3 | 3/3 | 3/3 |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local proof covers the supplied reference chain and immediate boundaries only. Model calibration remains unmeasured.
