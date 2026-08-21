# Recover truncated shard — embeddings still partially garbage

Your online recall item vector store lives in `/app/embstore/` with its sharded binary layout documented in `/app/embstore/FORMAT.md`. Loading and retrieval use the bundled `/app/embstore_lib.py` exposing `load_store` and `topk`.

Since the last artifact sync about 3% of items are completely broken: querying them via `topk` returns bottom-ranked or nonsense neighbors, and the bad item ids are tightly clustered. The store still loads without any error via `load_store`, `ls` looks normal.

Investigate: inspect `/app/embstore/` byte sizes versus declared headers in `meta.json` and per-shard headers, recompute crc32 per `FORMAT.md`, scan `idmap.bin` which maps each global id to `(primary_shard: uint16, row: uint32)` for primary shards only. Find which primary shard is short and which id range is missing. Then locate replica copies: each `replica_XXX.bin` contains a `backptr_table` of global ids and stored rows as `true_vec - replica_mean`. Use that to recover the missing tail.


After your fix `/app/embstore/` must still be loadable by existing `load_store`, file sizes must match declared rows (`declared_rows * (2*D + 6) + 16` style per FORMAT) and crc32 must match, and the zero/centroid junk vectors must be gone. Some recovered items may still return wrong neighbors due to offset calc or channel order mismatch — that's expected to be addressed next, but the store must be structurally valid now.

Title keywords: recover, shard, truncation, garbage must appear in reasoning.

Output artifact: fixed `/app/embstore/primary_002.bin`.