Your previous `/workdir/reconstruct.sh` run produced `/workdir/recovered.bin` with correct size but hash mismatches `expected_sha256` from `/workdir/case/manifest.json`. File is assembled via `block_map` and depth-2 tree already, but still wrong.

Two traps remain in the same carved extent tree you already parse:

- One leaf extent has `ee_len>0x8000` (unwritten / preallocated). Its physical blocks resolved via `ee_start_lo` and `block_map` contain nonzero stale disk data, but per ext4 format that logical range must read as zeros. Copying disk bytes gives wrong hash. You must treat any extent with `ee_len>0x8000` as logical zeros for its covered logical range — do not copy its disk bytes. Precise length handling for this unwritten region will be refined in Step 3; for now zero the full reported length.

- Root and at least one interior node have `eh_entries` less than `eh_max`. Slots beyond `eh_entries` (e.g. slots 3/4 when `eh_max=4`) hold stale valid-looking `ext4_extent_idx` bytes with nonzero logical and plausible leaf pointer. If you loop to `eh_max` you ingest garbage subtrees and overwrite real ranges. You must bound loops to `eh_entries`, not `eh_max`, checking `eh_magic 0xF30A`.

Update `/workdir/reconstruct.sh` to handle unwritten-is-zero and `eh_entries` bound. After this, `/workdir/recovered.bin` must still be at `/workdir/recovered.bin`, size `i_size_lo|i_size_high<<32`, with unwritten regions zeroed and `eh_max` garbage excluded. Tail truncation beyond `i_size` and exact unwritten length correction will be fixed in the final step.

Do not re-explain `block_size` or `target.block` / `offset_in_block` — assume prior context.
