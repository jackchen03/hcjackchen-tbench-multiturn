# PostgreSQL cast, skew, and partition pivot

This three-turn task carries `/app/query.sql`, `/app/schema.sql`, the
`/app/run_query.sh` interface, and fixed verifier-owned buffer budgets. Step 1
repairs an expression/type mismatch and access path. Step 2 must retain exact
ordinary lookups while changing the physical design for a 40%-skew workload.
Step 3 is a genuine override: a history-dominated range report must move to the
new RANGE-partition layout while point lookups remain correct.

All graders provision 500,000-row databases and replay candidate SQL on fresh
per-case copies. Expected rows come directly from generator-loaded pristine
tables, independently of candidate files. Public and hidden customer-id ranges
are disjoint. Plans are checked from JSON `EXPLAIN (ANALYZE, BUFFERS)`; shared
hit and read blocks are summed over every plan node.

Both boundaries permit compatible supersets, so over-execution is
contract-justified `NOT_REQUIRED`. The important transition negatives are
under-execution: the step-1 plain index breaches the skew budget, and the
step-2 unpartitioned layout breaches the growth/pruning contract.

## Completion rates

| Agent | Step 1 | Step 2 | Step 3 | Whole task |
|---|---:|---:|---:|---:|
| No-op | unmeasured | unmeasured | unmeasured | unmeasured |
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence, when present under `.validation/`, establishes bundle
correctness only; model difficulty and cloud validation remain unmeasured.
