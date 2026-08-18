# Add query path

Your /app/indexer from last step now byte-matches the legacy writer, so we can build correct indexes. Next we need a fast path to answer point queries directly from those index files without rebuilding the bitmap from original positions.

Build a new executable at /app/query that takes the index file path as argv[1]. It reads from stdin JSON like {"queries": [pos0, pos1, ...]} where each query is a bit position to test, and it writes to stdout JSON like {"results": [bool, ...]} where each bool indicates whether that position is set to 1 in the bitmap represented by the index file. Parse the index file you already reverse-engineered – do not re-derive answers by re-reading original JSON inputs or calling the reference.

Keep your previous binary at /app/indexer at same path with same invocation: stdin JSON {"nbits": N, "positions": [...]} raw bytes stdout, still byte-identical to /app/reference/bitmap_index. Hidden tests will first use your indexer to produce an index then run your query binary against it on held-out bitmaps and queries.

The title keywords add query path relying exact index build must appear. You already have area and conventions from last step, so do not re-derive container layout – reuse /app/indexer path and format you recovered.
