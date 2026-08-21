# Pivot to seq-order redistribution on split

Even after handling splits and overflow chains, a class of keyfiles still mismatches byte-for-byte: those where a bucket's overflow holds a key inserted earlier than some primary slot key, and then that bucket splits. Your current redistribution re-inserts keys in physical page scan order, but the byte diff shows the old engine re-collected all keys of the splitting bucket and re-sorted them by insertion sequence before re-hashing.

We crafted `/app/samples/reorder_case.key` where an overflow key has smaller seq than a primary key — after forcing a split, the two variants produce different bucket layouts. Hexdiffing the two `index.bin` files before and after the split proves physical-scan order is wrong.

Fix `/app/hashbuild` (same path, same usage) to collect all keys of the bucket being split (primary plus every overflow page) and re-sort by their seq field (true insertion order, visible as second field in slot) before re-hashing with `h_{L+1}` into the old and new image buckets, preserving newest-first overflow insertion throughout. After the fix, the previous physical-scan redistribution path must be removed — it is incorrect for this dialect.

Also write `/app/seq_reorder_proof.json` containing a minimal reproduction: fields `trigger_bucket` (int bucket id you observed reordering on), `keys_before_split` (list of keys in that bucket before split in physical order), `seq_order` (same keys sorted by seq), `physical_order` (same keys in physical page order), `note` (string explaining that seq-sort differs from physical scan). This file documents the probe that revealed the final quirk.

After this fix, your `/app/hashbuild` must produce byte-identical outputs to `/verifier/hashload` for all held-out keyfiles, including those that force multi-overflow reorders, and must be self-contained without calling the oracle at runtime. Final verification will run your binary while `/verifier/hashload` is absent.
