Your previous `/workdir/reconstruct.sh` run produced `/workdir/recovered.bin` with correct size but hash mismatches `expected_sha256` from `/workdir/case/manifest.json`. File is assembled via `block_map` and depth-2 tree already, but still wrong.

Two traps remain in the same carved extent tree you already parse:

- One leaf extent has `ee_len>0x8000` (unwritten / preallocated). Its physical blocks resolved via `ee_start_lo` and `block_map` contain nonzero stale disk data, but per ext4 format that logical range must read as zeros. True data length for that extent is `ee_len - 0x8000`. Copying disk bytes gives wrong hash.

- Root and at least one interior node have `eh_entries` less than `eh_max`. Slots beyond `eh_entries` (e.g. slots 3/4 when `eh_max=4`) hold stale valid-looking `ext4_extent_idx` bytes with nonzero logical and plausible leaf pointer. If you loop to `eh_max` you ingest garbage subtrees and overwrite real ranges.

Fix `/workdir/reconstruct.sh` to handle both: zero the unwritten extent's logical range (do not copy its disk bytes despite nonzero on disk), and bound every header iteration to `eh_entries` not `eh_max`. Keep the `block_map` resolution, depth-2 traversal via `eh_magic 0xF30A`, `i_flags` `EXT4_EXTENTS_FL 0x80000` check, `i_block`, `ee_block`, `ee_len`, `ee_start_lo`, `i_size_lo` / `i_size_high` handling you already have. After fix, `/workdir/recovered.bin` should still be written to same path and be closer to `expected_sha256`.

Do not re-explain `block_size` or `target.block` / `offset_in_block` — assume prior context.
