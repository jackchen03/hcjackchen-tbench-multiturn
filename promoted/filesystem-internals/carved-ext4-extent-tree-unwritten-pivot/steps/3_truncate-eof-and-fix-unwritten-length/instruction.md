Profiled traces from the carved ext4 extent tree reconstruction show your current `/workdir/reconstruct.sh` still produces `/workdir/recovered.bin` with right size but hash off by tail bytes and unwritten region length — this pivot fixes the final two traps:

- `recovered.bin` is allocated as `i_size = i_size_lo | i_size_high<<32` zero-filled, holes already zero, but last extent extends beyond `i_size` (EOF preallocation). Tail beyond `i_size` must be truncated — file must be exactly `i_size` bytes, not concatenated extents length. `FORMAT.md` says file size authority is `i_size_lo`/`i_size_high` and logical zeros are mandated for holes and unwritten.

- Unwritten detection is still incomplete: you zeroed `ee_len` bytes, but true length is `ee_len - 0x8000` (because `0x8000` flags unwritten). You must compute `n = ee_len - 0x8000` when `ee_len>0x8000` and zero only `n` blocks at logical offset `ee_block`, not full `ee_len`. Copying stale nonzero disk bytes from `ee_start_lo` resolved via `block_map` must be removed.

Switch: old code that treated every extent as direct block copy without zeroing must be dropped — tail beyond `i_size` must not be written, unwritten extents must be logical zeros per `FORMAT.md`. Also ensure loop bound remains `eh_entries` not `eh_max`, checked via `eh_magic 0xF30A`, `EXT4_EXTENTS_FL 0x80000` in `i_flags`, using `i_block`, `ee_block`, `ee_start_lo`.

Update `/workdir/reconstruct.sh` to implement truncation to `i_size_lo`/`i_size_high` and correct unwritten length `ee_len - 0x8000`. After this, `/workdir/recovered.bin` sha256 must match `expected_sha256` from `/workdir/case/manifest.json`. Direct block copy without zeroing unwritten must be absent; loop to `eh_max` must be absent.
