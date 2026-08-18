# Build commit index

Your previous /app/recover from step 1 now produces the correct committed set on samples and on held-out disjoint sites.

Operations now needs fast point lookup of where each committed transaction actually committed in the log. The committed set text is not enough — they need an index sidecar that maps each committed xid to its commit LSN and is byte-exact against the reference.

Keep your /app/recover at the same path and keep its existing contract /app/recover <dataDir> <outputFile> writing sorted decimal IDs one per line \n. Don't re-derive the WAL chain layout from scratch; you already have area and conventions from FORMAT.md and the block continuity you discovered.

Add a sidecar: whenever /app/recover <dataDir> <outputFile> runs, it must also write a file at /app/commit.idx containing the committed transactions index in the sorted format. The exact byte layout for this step is defined in /app/INDEX_FORMAT.md section "Sorted commit index (step2)": magic 0x43494458 CIDX, version 1, num_entries, header CRC, then sorted ascending by xid entries of (xid u64 BE, commit_lsn u64 BE) where commit_lsn is byte-LSN where that transaction's COMMIT record starts per true lifetime discovered by your continuity walk.

We will run your recover on new held-out crash sites and check that /app/commit.idx exists, magic matches CIDX 0x43494458, number of entries matches txt lines, sorted ascending, each xid's commit_lsn matches ground truth commit start LSN from true recovery, and file is byte-exact vs /verifier/build_sorted_index oracle.

Use your carried conventions and file from previous step; don't re-pin block header fields or record chain rules.

Title keywords for this step: build, commit, index, sorted. Must reference /app/commit.idx, /app/INDEX_FORMAT.md, commit_lsn, CIDX, sorted.
