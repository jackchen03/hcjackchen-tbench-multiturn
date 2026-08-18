# Pivot to canonical v2

The fleet upgraded to engine v2. The quirks you reverse-engineered — XOR delta, conditional dead-slot prune, bespoke SET_SLOT-first intra-LSN tie-break — were bugs and are now fixed. New witness pairs from the upgraded engine live under /app/samples_v2/caseNN, each with heap.bin, wal.bin, recovered.bin using canonical replay semantics. Your old quirky /app/replay now produces wrong bytes on these v2 cases.

Switch /app/replay to canonical v2 behavior. Don't keep the old quirky path: OVERWRITE must directly overwrite payload bytes at arg, DELTA must also directly overwrite (not XOR nor add), SET_SLOT writes slot entry, PRUNE must unconditionally zero length bytes starting at current slot[k].tuple_off regardless of dead flag, and within one LSN records must apply in stream order (not SET_SLOT-first/PRUNE-last). pageLSN filtering (replay only lsn > pageLSN, advancing pageLSN per record) stays canonical.

You must also write /app/REPLAY_VERSION file containing exactly "v2\n" (lowercase v, digit 2, newline). And ensure /app/replay_audit when re-run over /app/samples_v2 still produces /app/replay_audit.json entries where prunes_fired equals prunes_evaluated (because prunes are now unconditional) and records_applied follows stream LSN order counting.

The old quirky logic must be removed — final /app/replay must not contain XOR modification for DELTA nor conditional check of flags bit0 for PRUNE nor the SET_SLOT-first tie-break ordering. Verification will assert absence of those old paths and byte-exact match against /app/samples_v2/caseNN/recovered.bin.

Body includes pivot, canonical, v2, /app/samples_v2, /app/REPLAY_VERSION, /app/replay, /app/replay_audit, /app/replay_audit.json, heap.bin, wal.bin, recovered.bin.
