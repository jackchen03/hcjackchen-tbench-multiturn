# Evict deleted and checksum — storage-layer fix

Deleted near-duplicates still crowd top-k and displace live twins even though navigation is now correct. Deleted items are still reachable despite correct navigation because they were never ejected from slot array — they remain within `[0,node_count)` and off the free-list, and `entry_point` was staled (now fixed) but free-list still stale.

You need to finish the compaction at storage layer: walk the free-list starting from `free_list_head`, splice all deleted physical slots onto it, adjust `node_count` down to live count so loader in `load_index` never visits deleted, ensure `entry_point` (already remapped) points to live slot, and recompute checksum per `FORMAT.md` so header counts/offsets stay self-consistent and `load_index` still reads clean.

Crucially: old approach of post-filtering deleted `item_id` at query time inside `annlib.py` `knn_search` or a wrapper must be removed — fix must be at storage layer not post-filter. The grader uses its own copy of `annlib.py`, so query-time filtering will not hide ghosts and will be caught. Also `version` field in header is a decoy — it's epoch-like but not load-bearing, `knn_search` ignores it and bumping version alone is not sufficient. Keep `/app/annindex/` layout valid per `FORMAT.md`.

Final state in `/app/annindex/index.bin` must: be loadable by `load_index`, yield expected recall ~0.95 on held-out queries over live set via `knn_search`, return zero deleted `item_id`s, have `free_list_head` chain covering all deleted slots, have `node_count` equal live count, and have valid `checksum`. Do not modify `annlib.py` or `FORMAT.md`. Absence checks: no deleted filtering code in `annlib.py`, no relying on `version` bump as fix.

Title keywords evict, deleted, checksum must appear.
