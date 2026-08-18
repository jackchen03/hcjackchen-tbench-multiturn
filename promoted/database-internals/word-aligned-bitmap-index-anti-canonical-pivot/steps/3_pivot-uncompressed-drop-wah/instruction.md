# Pivot uncompressed drop wah

The word-aligned compressed index path you built is now deprecated. Check /app/migration.log – profiling shows decoding overhead outweighs size saving for our workload and the downstream cache that required the WAH dialect has been decommissioned. New reference at /app/reference/bitmap_index_v2 writes a different uncompressed bit-packed format with no fill words and no header index.

Update your executable at /app/indexer to byte-match /app/reference/bitmap_index_v2 instead. Same invocation: stdin JSON {"nbits": N, "positions": [...]} raw bytes stdout, but now identical to v2 for every input, not to the old dialect. Probe /app/reference/bitmap_index_v2 freely to learn its layout – it uses header 'U','B' plus N and raw words, tail zero-padded uncompressed, not the old WAH tags.

Remove the query path: executable at /app/query must no longer exist, and your new indexer must not contain old WAH-specific logic – tests will assert absence of demotion threshold, trailer inherited pad, fill-1 position-list header, and LITERAL-RUN / FILL-0 / FILL-1 tag handling. The RUN-length compressed path poor hit rate on new traces motivated this change to uncompressed.

The title keywords pivot uncompressed drop wah must appear. Motivation is legible via /app/migration.log and new reference /app/reference/bitmap_index_v2. Preserve stdin JSON to stdout bytes contract but produce uncompressed bytes.
