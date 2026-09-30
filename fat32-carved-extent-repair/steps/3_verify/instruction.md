Steps 1 and 2 left the image and /work/files_manifest.json in place; start from them.

Copy each manifest file out with `mcopy` or identical-bytes reads, run `SELECT COUNT(*) FROM records;` with `sqlite3` on each file, check every `sha256sum` against the manifest, then write /work/outcome.txt with exactly `FS_CLEAN ROWS=<n> HASHES_OK` plus trailing newline, where <n> is the decimal sum of the per-file counts; the image must also pass `fsck.vfat -n` clean. Also leave an executable /work/verify.sh invoked as `bash /work/verify.sh <repaired.img> <manifest.json> <outcome.txt>` that reproduces the outcome for any image plus manifest from this chain and exits 0.

At grade time the checks re-run on this image and `bash /work/verify.sh` is invoked on a held-out image plus manifest with different row totals; listing alone does not pass.
