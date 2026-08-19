Profiled forensic traces from the ext4 repair show your current `/workdir/repair.sh` still produces self-consistent but byte-different images — `fsck.ext4 -n` clean, but hidden byte-compare to pristine original fails by inode table bytes and dirent bytes.

The old strategy that rewrote `i_links_count` to counted refs (Pass-4 style) and rewrote `file_type` to match new target (Pass-2 style), including running `e2fsck -fy`, is forensically wrong for this damage class. The pristine image was fully consistent before, only 4-byte `inode` field of one dirent overwritten. Restoring that field alone yields exact original; touching `i_links_count` or `file_type` yields different bytes and leaves one path forever resolving to wrong inode.

Switch to different recovery strategy: only overwrite impostor dirent's 4-byte little-endian inode field back to under-referenced inode identified via `file_type` vs `i_mode` mismatch. Drop old logic that writes `i_links_count` or writes `file_type`. Check `FORMAT.md` says mandate is byte-identical restore, not self-consistency — file size authority is not `i_links_count` rewrite.

Old direct rewrite of link counts without restoring dirent must be removed, and old file_type fix must be absent. Keep carried conventions: raw-scan every directory block, count refs per inode, over-referenced vs under-referenced, impostor is UNIQUE dirent whose `file_type` disagrees with target mode, mode of impostor's `file_type` matches under-referenced. Touch nothing else.

Update `/workdir/repair.sh` to implement this pivot. After it runs, `/tmp/out.img` from `/workdir/repair.sh /opt/tbench/holdout/caseX/broken.img /tmp/out.img` must be byte-identical to original, `fsck.ext4 -n` clean, every dirent `file_type` matches its target mode, every `i_links_count` equals counted refs, without you modifying any `i_links_count` or `file_type` byte.
This step must handle drop correctly.
