# Finish compaction — index loads clean but knn misses live

Your recall index lives in `/app/annindex/` with its on-disk layout described in `/app/annindex/FORMAT.md`. Loading and searching use the bundled `/app/annindex/annlib.py` which exposes `load_index` and `knn_search`.

Since the crash during compaction the symptoms are: `load_index` opens `/app/annindex/` without any error, `ls`/`stat` look normal, but running `knn_search` on queries from the sample set under `/app/samples/` shows recall@10 dropped from about 0.95 to around 0.6, and results sometimes contain item ids that were deleted weeks ago (near-duplicates of live items that now crowd top-k and displace their live twins).

Investigate: write a small reproduction using `load_index` and `knn_search` from `annlib.py` on the sample queries, compare against brute-force over the live set, observe the recall drop and deleted surfacing. Then repair `/app/annindex/` in place.

The compaction left a remap table at `remap_table_off` that maps old physical slot ids to new slot ids. The slot array starts at `slot_array_off` and each slot contains `item_id` and `neighbor_ids`. `entry_point` in the header is a physical slot id. To finish the interrupted compaction, finish applying that remap table: for every slot parse its `neighbor_ids` and replace each entry via the remap table from `remap_table_off`, remap `entry_point` via the same table, and make the file self-consistent per `FORMAT.md` so `load_index` still reads it clean.


Title keywords: finish and compaction must appear in your reasoning but output remains the fixed `/app/annindex/index.bin`.