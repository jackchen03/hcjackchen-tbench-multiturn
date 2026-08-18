# Handle build-side byte threshold recursive partitioning

Your previous /app/hashjoin matches /app/refjoin on fit-only inputs, but it drifts as soon as build data gets larger. On those larger inputs the row multiset is still correct (multiset equality holds, no row missing or extra), yet the byte stream order diverges from /app/refjoin.

Probe /app/refjoin with varying build sizes and column widths. The recursion trigger is not tuple count and not probe side — it keys off build-side spilled bytes. When a build partition's serialized byte size crosses a threshold T, refjoin recursively repartitions both its build and probe tuples with a child hash derived from the parent by folding the recursion level into the mix, up to a max depth. Partitions, including child partitions, are processed in spill-completion order (order of last build tuple), not ascending id.

Extend your existing /app/hashjoin to implement this. Keep the spill-completion ordering and fit emission probe-scan times build-insertion you already discovered, without re-stating FORMAT.md or re-deriving P. After this step, /app/hashjoin must byte-match /app/refjoin on inputs that cause exactly one level of recursion (some build partitions cross T, their child sub-partitions all fit).

The title keywords byte, threshold, recursion, and partition must be relevant. Do not re-implement from scratch — adapt your prior artifact.

Output contract: same executable path /app/hashjoin, same stdin JSON -> argv[1] file contract per /app/FORMAT.md, now byte-matches refjoin on both fit-only and single-level-recursion held-out inputs.
