Now that you know which pages are stale, implement the actual recovery.

Using the same crash scene format you already diagnosed (files `heap.bin`, `dwb.bin`, `wal.bin` under a data directory, layouts in `/app/FORMATS.md`), write an executable `/app/recover` with usage `/app/recover <data_dir> <output_file>`.

It must compute for every page the correct content that should be kept after the crash, and write the fully recovered heap (the corrected `heap.bin` byte stream, same page count and order) to `<output_file>`.

Correct recovery per page:
- From WAL, compute committed batch set (`BATCH_COMMIT` present) and per-page `target_lsn` = max `page_lsn` among `PAGE_WRITE` records in committed batches, null if page never touched.
- Candidate images: in-place heap page eligible only if its CRC32 over first 508 bytes matches trailing u32 LE; plus every DWB ring slot holding this page that belongs to a committed batch and whose embedded page CRC is valid.
- Install the candidate whose `page_lsn == target_lsn`. If `target_lsn` is null, keep max-LSN eligible candidate (usually in-place). If no eligible candidate, keep in-place bytes as-is.
- Crucial: CRC is only for eligibility, never for deciding currency. And do not pick the ring's newest `slot_seq` or max `page_lsn` across all slots — the crash batch that never got a `BATCH_COMMIT` left post-images in the ring with highest `slot_seq` and higher `page_lsn` than committed, which must be ignored.

Your previous `/app/triage` and `/app/report.json` can stay, but this binary must work on its own for any crash scene with disjoint `row_id`, page numbers, batch_ids, and LSNs — not just `/app/data/`.