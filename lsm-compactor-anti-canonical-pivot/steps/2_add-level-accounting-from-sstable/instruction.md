# Add level accounting from SSTable

Your previous `/app/compact` now byte-matches `/app/refcompact` for arbitrary run sets — it reproduces the anti-canonical dialect exactly.

The compaction service now needs per-file level accounting that is derived from the actual SSTable file you just produced, not just from input counts. Don't re-derive the chain layout or container format from scratch; you already have the area and conventions from FORMAT.md and your previous binary.

Input JSON now includes two extra fields: `"target_level": int` and `"level_sizes": [int]` (current size per level). Your program usage changes to `/app/compact <sst_path> <accounting_json_path>`: first arg is still the SSTable output path (must still be byte-exact vs `/app/refcompact`), second arg is a JSON file you must write.

The accounting JSON must be computed by reading back the SSTable file you wrote, parsing it per FORMAT.md, and emitting:
- `target_level`: same as input
- `file_size`: actual byte size of the SSTable file on disk
- `num_data_blocks`: number of data blocks counted from the index block / footer
- `num_entries`: total number of entries (both put and del) in data blocks
- `num_tombstones`: number of deletion entries that survived compaction (per your dialect)
- `first_key_b64`: user_key of the first entry (base64)
- `last_key_b64`: user_key of the last entry (base64)
- `updated_level_sizes`: copy of input level_sizes where entry at target_level is incremented by file_size

Keep `/app/compact` at the same path and keep writing the SSTable exactly as before. The accounting must rely on the carried SSTable artifact — if your blocks are canonical, block count and file_size will differ and accounting will be wrong even if entry counts look right.

Samples for this step are under `/app/samples/` with golden SSTables plus sample accounting JSON computed from those golden files.
