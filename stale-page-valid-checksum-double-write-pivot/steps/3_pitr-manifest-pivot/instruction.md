We traced production crashes further. The stale page with valid checksum problem from the double-write buffer is now a compliance issue. Recovering to latest committed is not enough — we need point-in-time recovery (PITR) to any committed batch, with an auditable manifest proving provenance. Also, the earlier patterns we relied on are unsafe: picking the double-write ring's newest `slot_seq` or using checksum CRC-validity to decide whether a page is current leaves either torn pages undetected or aborted-batch images installed, because the aborted batch's post-images have valid checksums, highest `slot_seq`, and higher `page_lsn` than the last committed version.

The previous recovery that always recovers to latest and assumes newest slot wins is too fragile to audit and fundamentally wrong under ring reuse. This is a pivot: switch to strict LSN-matched selection keyed on WAL committed set, and drop the checksum-as-currency and newest-slot heuristics. The old stale-page detection that relied on CRC alone must be removed from the new binary.

Write an executable `/app/recover_pitr` with usage `/app/recover_pitr <data_dir> <target_batch_id> <output_heap>`. It must:
- Parse `wal.bin` to compute committed batches, and only consider batches with `batch_id <= target_batch_id` and committed.
- Compute per-page `target_lsn` as max `page_lsn` among `PAGE_WRITE` records in that filtered committed set (null if never touched up to target).
- Rebuild heap exactly as before but using this PITR target: for each page, select candidate (in-place if CRC ok plus DWB slots from filtered committed batches with valid CRC) whose `page_lsn == target_lsn`, else max eligible if `target_lsn` null.
- Write recovered heap bytes to `<output_heap>`.
- Additionally write `/app/manifest.json` (same dir, fixed path) with provenance for every page:
```
{
  "target_batch_id": int,
  "target_lsn_per_page": { "page_no": target_lsn_or_null },
  "pages": [
    {
      "page_no": int,
      "selected_source": "heap" | "dwb",
      "selected_slot_seq": int | null,
      "selected_batch_id": int | null,
      "selected_page_lsn": int,
      "target_lsn": int | null,
      "in_place_crc_ok": bool,
      "was_stale_valid": bool
    }...
  ],
  "committed_up_to_target": [batch_id asc],
  "aborted_up_to_target": [batch_id asc]
}
```
Pages sorted by `page_no`. `was_stale_valid` true iff in-place CRC ok and `in_place_lsn < target_lsn`.

Requirements:
- Do not install any DWB image from an aborted batch or batch with `batch_id > target_batch_id`, even if its `slot_seq` is newest or its `page_lsn` is higher.
- Do not use CRC to decide currency — CRC only gates eligibility of in-place candidate.
- After this step, `/app/recover_pitr` must be the authority; keep `/app/recover` from last step for regression (its latest-batch behavior must still match ground truth on random scenes), but remove any code that picks max `slot_seq` or relies on CRC alone from `/app/recover_pitr` source (absence will be checked by scanning source for such heuristics).

This completes the chain: diagnosis, latest recovery, then strict PITR with audit manifest and removal of the old newest-slot / CRC-currency logic.
