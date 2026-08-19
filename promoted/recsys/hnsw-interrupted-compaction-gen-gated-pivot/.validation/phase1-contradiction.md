# Phase-1 contradiction

Phase 2 stopped before bundle implementation because the required Step-1-to-Step-2 state transition cannot produce the declared Step-2 result.

- Step 1 explicitly requires applying the remap table to `neighbor_ids` for **every** slot.
- Step 2 states that this uniform operation double-remapped the already-migrated `generation==1` half and scrambled its adjacency.
- Step 2 then explicitly requires: for `generation==1`, leave `neighbor_ids` untouched; only remap `generation==0` slots.

Because the chain carries the same in-place `index.bin`, the `generation==1` neighbors entering Step 2 are already double-remapped and corrupted by the mandatory Step-1 operation. Leaving them untouched cannot restore their pre-Step-1 new-space values. The declared Step-2 algorithm has no pristine copy, inverse-remap rule, journal, or original-neighbor metadata from which to repair them.

The dossier notices the need to correct the double-remap damage but its oracle sketch again says to leave `generation==1` slots unchanged. Those requirements cannot both hold. Phase 1 must either preserve recovery metadata/pristine neighbors, specify an inverse remap for those slots, or change Step 1 so it does not destructively double-remap them.
