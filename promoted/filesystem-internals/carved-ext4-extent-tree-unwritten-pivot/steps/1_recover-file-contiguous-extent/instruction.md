We are recovering data from a dead SSD. The vendor gave us only a shuffled carve: a binary blob at `/workdir/case/blob.img` and a manifest at `/workdir/case/manifest.json`. No superblock (no `0xEF53`), so `debugfs`, `dumpe2fs`, `fsck.ext4` refuse to open it — you must parse raw bytes.

The manifest contains `block_size` (4096), `inode_size` (256), `block_map` which maps each physical block number to its byte offset in the blob (the blob is shuffled, offset != block*`block_size`), `target` with `target.block` (physical block holding the inode-table fragment) plus `offset_in_block` (byte offset of inode 12 inside that fragment), and `expected_sha256` — the correct file's hash for self-check.

Inside that fragment at `target.block` + `offset_in_block` lies inode 12 (256 bytes): `i_flags` at inode offset 32 must have `EXT4_EXTENTS_FL 0` set, `i_block` at offset 40 (60-byte area) holds the carved ext4 extent tree root, `i_size_lo` at offset 4 and `i_size_high` at offset 108 give the file size. The root header has `eh_magic 0xF30A` and `eh_depth=2` (root -> index -> leaf). Leaf entries have `ee_block` logical offset and `ee_start_lo` physical start.

The natural first attempt copies extent blocks directly assuming blob offset = block*`block_size`. That is WRONG because the blob is shuffled — you must resolve every physical block through `block_map` to get the true blob offset.


Note: `FORMAT.md` in the case directory describes overall layout but does not give the fix.