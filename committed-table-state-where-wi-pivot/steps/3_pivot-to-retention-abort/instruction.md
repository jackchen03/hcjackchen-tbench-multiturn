The consumption semantics you shipped proved too error-prone for retry workloads that reuse the same label.

Profile we just captured shows why: a transaction marks label `a` twice, unwinds to `a`, then unwinds to `a` again to retry. Under the old consumption rule the first unwind consumes the topmost `a`, so the second unwind incorrectly resolves to an older same-named mark and drops extra rows that should have survived. For jobs that retry with the same label this causes data loss. Leadership is dropping the old resolution entirely.

Byte format stays the same, but adjudication changes. New spec is in `/app/FORMATS_V2.md` — read it — and a new oracle for this version lives at `/app/gold_replay_v2`, usage `/app/gold_replay_v2 <log> <out>`, with new samples in `/app/samples_v2/` (each `.log` with `.out`).

Changes versus v1:

- `UNWIND(label)` now RETAINS the target mark: pop only marks above the topmost matching label, keep the target itself on the stack. Re-unwinding the same label hits the same mark again.
- `UNWIND(label)` to a missing or already-popped label now ABORTS the whole transaction (treat as `END_BAD`, exclude all its records), instead of being a no-op.

Update `/app/replay` to implement v2 and remove the old v1 consumption/no-op path. Hidden tests will assert absence of the old behavior:

- A log where v1 consumption would drop an extra key by resolving to an older mark, but v2 retention must keep it.
- A log where v1 no-op would keep a transaction, but v2 abort-on-miss must drop it entirely.

If you keep a fallback that still does consumption or no-op, those probes will fail. Output format stays identical: `<key> <value>` per line sorted ascending, `\n`, no header, empty file if empty, written to `<output_file>` given on command line.

`/app/apply` can stay as you built it, but `/app/replay` is the graded artifact now and must not support both versions via a flag.
