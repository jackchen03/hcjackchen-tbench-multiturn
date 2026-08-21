You have an ext4 filesystem image at `/work/disk.img` that looks healthy at first glance: `ls` and reading files return data without error. In reality it is corrupted.

One regular file is cross-linked - its extent points to a physical block that belongs to another file's contiguous extent, so reading it returns that other file's data. Its real original block is still allocated in the block bitmap but unreferenced - a leaked block. `fsck.ext4 -n /work/disk.img` reports a multiply-claimed block and an unreferenced block. Its automatic repair would clone the shared block and free the leaked block, leaving the victim file permanently pointing at the wrong bytes and destroying its real data. Do not rely on that.

A pair of same-class images is in `/work/example/` to help you understand the class: `/work/example/broken.img` is broken the same way, `/work/example/original.img` is its correct pre-corruption version. Their size, block numbers, and content differ from `/work/disk.img`, so do not hardcode offsets.

The victim's original data block can be identified deterministically: the victim inode's extra area (bytes past 128, `i_extra_isize` field) contains at offset 0 a 4-byte little-endian CRC32-IEEE of its original data block content. Computing CRC32 of the leaked block must match this stored checksum — this distinguishes it from any other leaked bytes.

In this step, repair `/work/disk.img` in place, without mounting (no loop, no mount, no fuse, no root), by editing bytes or using tools that work without mounting. After repair, every file must read back its true original bytes, no file content lost or changed except fixing the victim, and `fsck.ext4 -n /work/disk.img` must report clean. Other files besides the victim must remain byte-identical to before.
