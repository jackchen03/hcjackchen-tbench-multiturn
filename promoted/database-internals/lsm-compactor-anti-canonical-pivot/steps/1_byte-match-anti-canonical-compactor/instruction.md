# Byte-match the anti-canonical LSM compactor

You are rewriting the compaction part of an LSM storage engine clean-room. You have a reference implementation binary `/app/refcompact` that was compiled earlier: give it a batch of input SSTable runs, it merges them into a new SSTable file. Your job is to write your own merger that produces byte-for-byte identical output to the reference for any input.

Put your program at `/app/compact` as an executable. It reads a JSON document from stdin describing input runs (`{"runs": [ [ {"key": b64, "seq": int, "type": "put"|"del", "value": b64}, ... ], ... ] }`), runs are oldest to newest, ordinal is 0-based index in `"runs"`, entries within a run are sorted by internal comparator. The exact input fields and the SSTable container format (data block prefix-compression with restart array, index block, footer, internal key layout) are in `/app/FORMAT.md` — follow it for container plumbing.

Write the merged SSTable to the path given as the first command-line argument.

The container format is given, but merge semantics like which entries survive and how each block's internal layout is cut are NOT fully documented in FORMAT.md. You must repeatedly run `/app/refcompact` on crafted inputs and diff the bytes to discover its real behavior, then reproduce exactly in your program. Consistency testing runs your `/app/compact` in a clean environment with unseen run sets while `/app/refcompact` is absent, so your program must be self-contained and not call the reference at runtime. A textbook LevelDB/RocksDB compaction (newest-wins, drop tombstones bottommost, fixed restart interval 16, canonical shortest separator) will be logically correct but byte-wrong.

Sample inputs and golden SSTables are under `/app/samples/` you can use to probe. Use `od -c`, `xxd`, `hexdump` on data and index blocks to isolate restart arrays and separators.
