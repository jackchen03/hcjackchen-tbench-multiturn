# Pivot to tiered GC — drop parity and accounting

Your parity-based GC and per-file accounting from last step now fail in production.

Fresh evidence:
- `/app/MANIFEST.log` shows `target_level=0` has overlapping SSTables in the next level (key ranges overlap). A recent compaction audit says GC is unsafe while next level overlaps — tombstones cannot be dropped even if their key appears only in odd-ordinal runs. The even-ordinal parity rule from `/app/refcompact` was an artifact of leveled L1 GC; tiered L0 must retain tombstones unconditionally (or at least without parity check).
- `/app/CENTRAL_ACCT.log` says per-file accounting JSON is now deprecated — centralized MANIFEST service owns level sizes, so your second-arg accounting file must not be produced anymore.

Switch dialect: your SSTable must now byte-match new reference binary `/app/refcompact_tiered` (present for probing) which keeps the same block splitting (512-byte target), same restart reset by shared-prefix threshold P=3, same index separator block-index parity rule, but changes tombstone survival to tiered-safe: keep all tombstones (or keep only based on keep_floor, without even-ordinal clause). Probe `/app/refcompact_tiered` on crafted inputs to discover the new exact rule — hexdiff will show extra tombstones retained vs old binary.

Remove the old logic:
- The previous path that checked input-run ordinal parity (`ordinal % 2 == 0` or even-run existence) to decide tombstone survival must go — it is wrong for tiered and must not be present in final `/app/compact`.
- The per-file accounting write path (second argv handling, metrics JSON, target_level accounting) must go — final usage reverts to single arg `/app/compact <sst_path>` only. If invoked with two args, it should not create the accounting file.

Keep `/app/compact` at same path, same container format from FORMAT.md, same B/C quirks, same output naming. Read FORMAT.md for block layout and use value handling. You need to keep restart threshold and separator parity logic, but drop parity GC and accounting.

This step is about generation-keyed? No — this step is about tiered GC pivot — body must mention tiered, overlapping, MANIFEST, GC, accounting deprecated, removal.
