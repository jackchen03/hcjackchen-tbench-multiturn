Your previous `/workdir/repair.sh` fixes the shipped `/workdir/case/broken.img` via `file_type` residual, but now fails additional held-out images where the same class of damage comes with different superblock layout — `block_size` 1024 vs 4096, different `inodes_per_group`, `inode_size`, `s_log_block_size`, GDT location, and different inode numbers for the hardlink pair and symlink.

For this step, extend the repair to handle the generic layout AND to perform the classic e2fsck Pass-2 / Pass-4 self-consistency fix as an intermediate milestone. This is intentionally different from the byte-identical restore-only final goal.

Assume carried context: raw directory block scan, superblock parsing, `file_type` 1 vs 7, `i_mode`, `inode:u32, rec_len:u16, name_len:u8, file_type:u8` dirent layout, `debugfs`/`dumpe2fs`/`fsck.ext4 -n`. Do not hardcode inode numbers.

Extend `/workdir/repair.sh` so after locating over-referenced and under-referenced inodes via counted refs vs `i_links_count` using the same `file_type` vs mode cross-check:
- Overwrite impostor dirent's 4-byte little-endian inode field back to under-referenced inode (same as Step 1).
- Also rewrite that dirent's `file_type` byte to match its new target's `i_mode` type bits (1 for `EXT2_FT_REG_FILE` regular, 7 for `EXT2_FT_SYMLINK` symlink) — classic Pass-2 style.
- Also rewrite every inode's `i_links_count` to equal its counted dirent refs — classic Pass-4 style.

Keep generic — same `<input> <output>` args, no hardcoded inode numbers, parse `s_log_block_size` for block size.

After fix, output must be `fsck.ext4 -n` clean, every dirent's `file_type` matches its target mode, every `i_links_count` equals counted refs, with those `file_type` and `i_links_count` writes present. This is self-consistent but NOT yet byte-identical to original — byte-identical pivot will drop those rewrites in the next step.
