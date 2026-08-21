We profiled the replay path from the first two steps. The one-shot consumption rule for MARK/UNWIND (pop the target mark itself) breaks on the new workload: retries reuse the same label many times, and the engine incorrectly resolves the second unwind to an older same-named mark or silently no-ops after consumption. This caused missed rollbacks and extra retained rows.

Leadership decided to drop the old conflict resolution entirely and switch to a standard retention model.

New v2 rules, effective from now:
- `UNWIND(label)` finds the topmost active mark with that label and undoes intervening data records, but now **retains** the target mark itself (pop only marks above it). Re-unwinding the same label hits the same mark again.
- `UNWIND` to a missing or already-popped label **aborts that transaction** (entire txn contributes nothing, like `END_BAD`), instead of being a no-op.

Update `/app/replay` to implement v2 semantics. Output format stays the same. The old consumption / no-op code path must be removed — we will probe duplicate-label re-unwind sequences and missing-label sequences; if you still exhibit the old behavior (resolving to older duplicate mark on second unwind, or ignoring a missing label) the test fails.

`/app/FORMATS_V2.md` Documents the byte layout unchanged but notes the new adjudication delta. New sample pair for v2 is under `/app/samples_v2/`. Your `/app/apply` from step 2 is no longer required, but `/app/replay` must now pass both the old empty/commit tests and the new retention/abort-on-miss tests.
