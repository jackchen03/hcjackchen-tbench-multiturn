# Phase-2 cumulative findings and contract map

Base commit: `448d1b0c2b40d4b800b094d5e23e092426d17747`

Frozen instructions were captured before implementation in
`instruction-sha256-before.txt` and match the external Phase-1 archive.

## Contract map

| ID | Step | Solver-visible contract | Planned verifier evidence |
|---|---:|---|---|
| S1-1 | 1 | `PRAGMA integrity_check` returns `ok` | Execute against repaired primary and hidden-family databases |
| S1-2 | 1 | Every committed order is durable in the main database | Compare full visible rows to a main-file-only copy and to a post-exit sealed reference |
| S1-3 | 1 | The `amount > 50` query runs through `idx_big` | Exact rows plus `EXPLAIN QUERY PLAN` on primary and hidden fixtures |
| S1-4 | 1 | `/app/recover.sh <dbpath>` repairs every fixture in the stated family | Execute the candidate on an independently generated, disjoint hidden family |
| S1-5 | 1 | Recovery report has exactly two keys and strict integer/string types | Parse and validate the candidate report after primary and hidden runs |
| S1-6 | 1 | `app.conf` is crash-safe | Require NORMAL/FULL and positive automatic checkpointing |
| S1-7 | 1 | Logical schema and index definitions are unchanged | Compare table metadata and normalized `idx_big` SQL to post-exit sealed truth |
| S2-1 | 2 | Zero-, one-, and two-argument replay interfaces work with documented defaults | Execute every argv form against restored copies of the carried S1 state |
| S2-2 | 2 | Highest `seq` wins and rerunning is stable | Independently fold sealed input after exit and compare exact row multisets after both runs |
| S2-3 | 2 | Final table is exactly S1 rows plus input max-seq rows | Exact full-row comparison on public and disjoint hidden families |
| S2-4 | 2 | Repaired state survives replay | Reassert integrity, exact config bytes, schema/index definition, indexed query, and prior rows |

Rows: 11. Mapped: 11.

## Transition matrix

| Field | 1_recover_index -> 2_idempotent_replay |
|---|---|
| Kind | Compatible additive context-following transition |
| Entry state | Actual S1-repaired `/app/store.db`, strict recovery report, and crash-safe `/app/app.conf` |
| Mutated | `/app/store.db` gains new rows and higher-sequence corrections |
| Overridden | Starter append-only `/app/replay.py` is replaced by max-seq idempotent replay |
| Read-only | `/app/app.conf`, `/app/schema.sql`, and replay input |
| Retired | Naive append-only behavior; WAL/SHM already retired by S1 checkpoint |
| Regressions | Exact S1 rows retained, integrity `ok`, config bytes preserved, logical schema/index retained, indexed big-order query exact |
| Under-execution | Starter replay fails on correction input and cannot be rerun |
| Over-execution | `NOT_REQUIRED`: S1 does not prohibit an already-hardened replay implementation; compatible supersets must remain valid |
| Future isolation | No S2 answer or expected multiset is present in the initial image |

## Findings inventory

| ID | Risk | Required closure |
|---|---|---|
| F1 | WAL deletion or implicit last-close checkpoint hides tail loss | Main-file-only durability check while a holder keeps the hidden WAL live |
| F2 | Integrity-only repair passes while committed rows remain WAL-only | Exact durable count and full multiset comparison |
| F3 | Config-only or index-only repair passes | Require all S1 layers together |
| F4 | Sample-ID hardcoding | Same grader on disjoint random family; behavior only, no source scan |
| F5 | Malformed or candidate-invented recovery report | Exact key set, strict non-bool integer, string method, independently read baseline |
| F6 | Truth exposed or computed before candidate exit | Root-only sealed input bytes; demoted candidate; post-exit derivation and temporal assertion |
| F7 | Naive/ignore replay loses corrections | Exact max-seq multiset and rerun stability |
| F8 | Replay damages prior repaired state | Full carried-state regression checks |
| F9 | Tests mutate the carried state during DO-NOTHING | Run probes on copies or restore sealed carried bytes in `finally` |
| F10 | Verifier source/fixtures visible to candidate subprocess | Root-only verifier/seal permissions and demoted candidate process |
