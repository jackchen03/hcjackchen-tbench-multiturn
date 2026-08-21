# Hash lookup pivot

Your sorted commit index from last step passes byte-exact checks but now fails profiling.

Fresh evidence from production trace replay: point lookups dominate 100:1 over scans. Binary searching the sorted array causes excessive page scans; the trace shows sorted array is too slow. We need to pivot index format to hash map and drop ordering work we added.

Switch your /app/commit.idx to the hash format defined in /app/INDEX_FORMAT.md section "Hash commit index (step3)": magic 0x43494459 CIDY, version 2, num_buckets fixed 64, buckets_offset, entries_offset, bucket array of head indexes (0xFFFFFFFF empty), entries array of (xid u64 BE, commit_lsn u64 BE, next_offset u32 BE chain, reserved) inserted in sorted-asc order for determinism so byte comparison works but hash structure provides O(1) lookup via xid % 64 chaining.

Remove the old sorted-only logic. The previous path that wrote magic 0x43494458 CIDX as the sole index format must go — it is wrong for this workload and must not be present in final /app/recover source. We will assert absence: your source must not write CIDX magic, must write CIDY magic 0x43494459, must contain bucket handling and next_offset chaining with 0xFFFFFFFF sentinel, and num_buckets 64.

Keep your existing /app/recover <dataDir> <outputFile> contract for txt committed set (sorted decimal one per line \n) — it must stay correct (regression check). Keep sidecar at same path /app/commit.idx but now hash format. Keep reading /app/FORMATS.md and /app/INDEX_FORMAT.md for layout and using commit_lsn from true continuity walk, not naive replay.

Motivation for pivot is legible: sorted array too slow on traces we just profiled, lookups dominate, switch to hash map and drop ordering assumption.

Title keywords: hash, pivot, lookup, commit, index. Must mention bucket, next_offset, 0x43494459, CIDY, 64, /app/commit.idx.
This step must handle hash pivot correctly.
Additionally, write a short JSON report of what you fixed to /app/3_hash-lookup-pivot_report.json.
