# Pivot to flat layout and drop old sharded artifacts

The sharded per-mean format with replica indirection proved fragile — truncation left `primary_002.bin` short by 60 rows plus its replica pointer table and crc, and cross-shard mean centering caused the verbatim-copy trap you just fixed. The team decided to drop the old layout.

Pivot: consolidate all embeddings into a flat contiguous layout at `/app/flat_embstore/` that stores true vectors directly with no per-shard means and no replica indirection. Write `/app/flat_embstore/embeddings.npy` as shape `(N, D)` float32 true vectors (un-centered), and `/app/flat_embstore/meta.json` with `num_items N`, `dim D`, `dtype=float32`. Provide a loader at `/app/flat_embstore/loader.py` exposing `load_store(path: str)` returning an object with the full matrix and `topk(query: np.ndarray, k: int) -> List[int]` brute-forcing over true vectors.

Then remove the old sharded artifacts under `/app/embstore/`: delete `primary_*.bin`, `replica_*.bin`, `idmap.bin`, `means.npy` — they must be absent after pivot. Keep `/app/embstore/FORMAT.md` and `/app/embstore/meta.json` and `/app/embstore_lib.py` untouched for archival but the sharded bin files must be gone so old path is not usable. The new flat store must yield same recall contract as the correctly re-centered sharded store: held-out queries' true nearest neighbors computed from original embeddings must match `topk` over flat store with >=0.90 recall@10.

Crucially, this is an overriding pivot: you must not keep primary/replica bins alongside the flat file. Absence checks will verify `/app/embstore/primary_002.bin`, `/app/embstore/primary_*.bin`, `/app/embstore/replica_*.bin`, `/app/embstore/idmap.bin`, `/app/embstore/means.npy` are all absent after step3. Only `/app/flat_embstore/embeddings.npy`, `/app/flat_embstore/meta.json`, `/app/flat_embstore/loader.py` must exist.

Title keywords: pivot, flat, drop must appear.
