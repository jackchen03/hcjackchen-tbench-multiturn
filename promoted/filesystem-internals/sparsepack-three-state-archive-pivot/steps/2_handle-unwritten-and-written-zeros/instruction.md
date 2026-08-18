Your previous `/app/mysparsepack` matches the reference on simple hole+written samples, but it still fails on files that read as zeros yet should not be type 0.

Two new classes appear in the same ext4 images you already handle:

- One extent has `ee_len > 0x8000` — the high bit flags an unwritten (preallocated/uninitialized) extent created by `fallocate`. On disk `ee_len - 0x8000` is the true length, it has allocated blocks via `ee_start_lo`, it reads as zeros exactly like a hole, but it is NOT a hole nor written: its archive type is `1` (unwritten), its `start_block`/`block_count` come from the extent itself not from a gap, and its bytes are excluded from the rolling `CRC-32` exactly like a hole. Written-zeros are the opposite trap: a genuinely written extent (type `2`) whose physical block is all `0x00` must stay type `2` with its zero bytes folded into the CRC — content inspection calling zero a hole misclassifies it.

Fix `/app/mysparsepack` in place — keep the `SPK1` header, inode `u32`, `i_size` `u64`, record count `u32`, record `type u8` `start_block u32` `block_count u32` CRC payload for type `2`, trailer `final_crc u32`, little-endian layout, and `mke2fs`/`debugfs`/`dumpe2fs` workflow you already have. After fix, archives must be byte-identical on images that mix hole, unwritten type `1`, and written with all-zero blocks. Do not re-explain `block_size` or `i_size` handling — reuse prior understanding.

The reference at `/app/reference/sparsepack` is still queryable for probing; use it to observe type trichotomy.
