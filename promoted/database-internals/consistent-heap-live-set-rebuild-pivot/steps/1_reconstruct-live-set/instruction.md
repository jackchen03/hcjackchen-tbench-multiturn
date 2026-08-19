# Reconstruct consistent live set

Your storage engine crashed mid fuzzy-checkpoint. After restart, some rows that were deleted long ago reappear when scanning the table, and the free-space map (FSM) is inconsistent — but if you look at any single heap page it looks internally valid, every row parses fine, and each FSM leaf also looks self-consistent laid out to the byte.

All crash artifacts live in /app. Exact byte layouts for heap.bin (4096-byte pages, slot {tuple_off, tuple_len, row_id, xmin, xmax} LE, payload region, USABLE fixed per page in FORMAT.md), fsm.bin, and commit.log (bare {rec_type, xid} with COMMIT/ABORT/CHECKPOINT, truncated, no tuple map) are in /app/FORMAT.md. A buggy old restorer /app/report_naive that reproduces both symptoms is in /app, and /app/samples/ has same-layout sample inputs plus known-correct live sets and FSMs for self-test.

Build an executable at /app/reconcile with usage `/app/reconcile <inputDir> <outputDir>`. Input dir has heap.bin, fsm.bin, commit.log with same layout as samples. For this step, focus only on the live set — ignore fsm.bin as witness for now.

You must parse heap slots and commit.log: drop any slot whose xmin did NOT commit (aborted insert), keep a slot whose xmax == 0 as live, and for xmax != 0 resolve against commit.log — if committed(xmax) mark dead, if aborted(xmax) keep live (rolled-back delete). This is canonical MVCC visibility. Emit `<outputDir>/live.txt` with surviving row_ids sorted decimal ascending one per line. You may also emit a placeholder fsm.bin but tests for this step only check live.txt (and that heap.bin/commit.log were actually parsed).

At this point you will still keep some rows that were deleted but not stamped (xmax==0 yet deleted) — that's expected for step1; samples show which rows those are when you diff your live.txt vs golden_live.txt.

Your binary must be self-contained, not depend on report_naive or samples at runtime, must read FORMAT.md layout and not hardcode sample row_ids.

Keywords that must appear: heap.bin, commit.log, FORMAT.md, live.txt, xmin, xmax, row_id, USABLE is not required yet but parsing is.