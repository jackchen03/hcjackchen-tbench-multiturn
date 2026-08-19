We have a self-developed heap storage engine that flushes pages in batches. During a flush it first writes pages into a double-write buffer ring file `dwb.bin`, appends metadata into a WAL `wal.bin`, then overwrites pages in place in `heap.bin`. Last week the machine lost power mid-batch.

After restart the table reads fine. But our consistency checker is alarming: some committed row versions from the WAL tail are missing from their heap pages, as if rows vanished. Weirdly, when we check those pages with the page-checksum tool, every checksum is good — `inspect.py` shows clean pages, `cat` and `hexdump` look intact. The current live heap under `/app/data/` is exactly this red state.

The crash scene is archived under `<data_dir>` with three binary files `heap.bin`, `dwb.bin`, `wal.bin`. Their byte layouts are defined in `/app/FORMATS.md`. You can also look at `/app/inspect.py` for how it parses page structure and CRC — but note it only checks CRC, it does not tell you whether a page is current.

Write an executable `/app/triage` with usage `/app/triage <data_dir> <output_file>`. It must read `heap.bin`, `dwb.bin`, `wal.bin` from `<data_dir>`, compute which batches committed according to the WAL, compute per-page `target_lsn` as the max `page_lsn` from `PAGE_WRITE` records belonging to committed batches, and classify each page.

The output file must be JSON with exact fields:
```
{
  "committed_batches": [batch_id sorted asc],
  "aborted_batches": [batch_id sorted asc],
  "pages": [
    {
      "page_no": int,
      "status": "torn" | "stale_valid" | "clean",
      "in_place_lsn": int,
      "in_place_crc_ok": bool,
      "target_lsn": int | null,
      "has_committed_dwb": bool
    } ...
  ]
}
```
Where `torn` means in-place page CRC fails, `stale_valid` means CRC ok but `in_place_lsn < target_lsn`, `clean` otherwise. `has_committed_dwb` true iff there exists a DWB slot for that page belonging to a committed batch with valid CRC and `page_lsn == target_lsn`. Pages sorted by `page_no` asc. Include all pages present in `heap.bin`.

More steps will follow; conserve disk and keep binaries. Focus only on triage and the report file for now — do not yet implement full heap recovery.