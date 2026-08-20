# MYFS image notes

- Images use 1024-byte blocks, 128-byte inodes, 8192 blocks per group, and 128 inodes per group.
- The primary superblock begins at byte offset 1024 and has magic `0xEF53` at offset 56 within the superblock.
- The primary group descriptor table begins at block 2. Each 32-byte descriptor starts with little-endian block-bitmap, inode-bitmap, and inode-table block numbers.
- Metadata for the groups in one flex is clustered at that flex's first group. Samples deliberately do not determine later stride and flex-index rules.
- `dumpe2fs`, `debugfs`, and Python's `struct` module can inspect images without mounting them.
