Profiling on delete-heavy production traces showed the ghost-slot allocator you just matched is now pure fragmentation debt — pages retain dead cells and stale slot entries forever until a split or merge rewrites them, so space leaks. The offset-based reader that required byte-exact replica has been retired; the new engine reads only logically via `dump-tree`, not raw offsets.

We need to pivot. Switch your existing `/app/btapply` (same path, same usage `/app/btapply <output file>` reading `I <key>` / `D <key>`) to produce a compact, ghost-free B+ tree index:

- On delete, eagerly remove the slot and compact the page — repack live cells to eliminate the gap, shift remaining slot pointers, decrement slot count so `nslots == nlive`, high-water retreats, no ghost bits ever set, no dead cells left behind.
- On insert, always append a fresh cell at the current high-water mark (no first-fit scan over dead ranges — there are none), fully packed.
- Merge triggered by live key-count falling below half of usable capacity, not by byte-fill; split point by key-count middle (median). Borrow still prefers right sibling first, then left, but after any borrow or merge pages are fully compacted.
- Output must be logically equivalent to the old tool on all operation streams (dump-tree key sets identical), but physically different: no ghost slots, no slack from reuse, smaller or equal file sizes on delete-heavy streams.

Also write `/app/migration_report.json` containing `old_ghost_pages`, `new_compact_pages`, `ghost_slots_removed`, `streams_migrated`, `compact_timestamp` — aggregate stats you measured when comparing old ghost files vs your new compact files across held-out streams. Remove any ghost retention, first-fit reuse, and byte-fill 40%/55% logic — hidden tests will assert that no page contains a ghost high-bit, that `nslots == nlive` everywhere, and that merge timing differs from the old byte-fill behavior.

Keep `/app/split_boundary.json` from the previous step intact.
