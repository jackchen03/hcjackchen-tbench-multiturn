We have a custom small storage engine that appends every change to a single key/value table into a binary transaction log in occurrence order. Ops replays the log to rebuild the table's final committed state, but the current rebuild is wrong: in a committed order, rows that the customer deleted and later modified during checkout are counted back in, and changes from transactions that never finished or were abandoned are mixed into the result.

The log itself is structurally clean binary — `od` / `hexdump` shows every record neatly, so flipping through raw bytes doesn't reveal what was over- or under-counted.

The environment has a reference replayer at `/app/gold_replay`. Usage: `/app/gold_replay <log_file> <out_file>` writes the true final committed state for that log to `<out_file>`. You can craft arbitrary logs and feed them to it to observe how it adjudicates various sequences, especially repeated rollbacks inside the same transaction and whether a transaction ends up committed or abandoned. Byte layout is in `/app/FORMATS.md` — it only documents the byte format with a one-line neutral gloss per record type; the actual adjudication rules should be inferred from `gold_replay` behavior, not from the doc. `/app/samples/` has some samples, each `.log` paired with a `.out` computed by `gold_replay`.

Deliver an executable at `/app/replay` with the same usage: `/app/replay <log_file> <out_file>` — read the binary log, compute the table's true final committed state, and write it to `<out_file>`.

Output format: one live key per line as `<key> <value>` (both decimal integers, single space), sorted ascending by key, newline-terminated `\n`, no header or extra content; deleted or non-live keys must not appear; if final table empty, output empty file.

During grading a set of unseen logs will be used (keys/values disjoint from samples), and `/app/gold_replay` plus `/app/samples` will be removed, so your program must fully implement the logic itself — no calling `gold_replay` at runtime, no hardcoding sample outputs.
