# Gen-gated remap fix

Your uniform remap from step1 double-remapped the already-migrated half and scrambled adjacency — held-out recall ~0.77 still RED. The file is in mixed per-node state.

Look at the per-slot `generation` byte you saw via hexdump: slots `[0,cut)` are `generation==1` with `neighbor_ids` already in new-space, slots `[cut,node_count)` are `generation==0` still old-space. Uniform apply corrupts the first half because a new-space id `< node_count` is coincidentally a valid old id that maps elsewhere.

Fix it gen-gated: for each slot if `generation==1` leave `neighbor_ids` untouched; if `generation==0` remap each neighbor id via table then set `generation=1`. Remap `entry_point` via table as well (it was still old-space). Keep using `/app/annindex/` same file, same loader `load_index`/`knn_search` in `annlib.py`, same layout from `FORMAT.md`. Title keywords gen-gated and remap appear.

You still will see deleted near-duplicates crowding results — that's expected for now, the stale deletion handling remains. Don't address deletion eviction yet. Just make navigation correct for live items and reach expected recall ~0.8+ after gate.
