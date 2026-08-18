After shipping lookup, perf traces show the branch that treats the trailing partial block's first value as a gap from the previous block, plus the extra trim to drop zero-pad duplicates to 8-byte alignment, is hot and confusing.

Writer team fixed the interrupted-flush path. The new index at /app/index_v2 uses a unified format: every block, including the trailing partial, starts with an absolute doc id (accumulator reset like full blocks), and the segment is tightly packed with no zero padding after the tail. The ordered posting values per tag are the same, only encoding changed.

Migrate to the new format: write /app/decode_postings_v2.py invoked as `python3 /app/decode_postings_v2.py <index_dir> <output_json_path>` that correctly decodes /app/index_v2 and outputs tag->ordered id list JSON. Running it on /app/index_v2 must match /app/index_v2/sample_tags_v2.json.

The legacy handling for continued-gap tail and pad-trim must be removed — the new decoder should treat all blocks as absolute-start and should not contain the old tail gap-continuation logic that added the previous last id to the first value of the trailing block. Also remove pad-zero handling.
