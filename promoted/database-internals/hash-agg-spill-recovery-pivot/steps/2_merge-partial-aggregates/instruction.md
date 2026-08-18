Your `/app/recover` from last step passes the sample but fails on the real crash site `/app/spill_crash/`. Some groups are too high (double-counted), some too low (drops the leftover run and the torn tail).

The crash happened mid-write of the top merge. Its header is intact so `header_crc` passes, but only a prefix is durable. A batch is durable for group g only if its index entry exists and `payload_off + payload_len <= filesize` (actual file length) — per `/app/FORMAT.md`. The torn top is durable only for that prefix; its inputs (level-1 batches and the never-merged last level-0 run) are still on disk undeleted. Each batch carries `partition_id`, `merge_level`, and `consumed_runs` listing which level-0 run ordinals of that partition it subsumes.

Fix it: for each partition, full run set is `0..max(consumed_runs)`. Per group, pick the frontier antichain — the highest-level durable batches whose `consumed_runs` sets are disjoint and union to the full set (e.g., group the top durably rolled up → frontier {top}; group past torn point → frontier {level-1 over {0,1}} ∪ {leftover level-0 {2}}). Combine frontier states with real combine (int-add SUM, set-UNION distinct). Keep same binary path `/app/recover` and same output contract (`\t` separated, sorted by `group_key`, `\n`).

More steps follow; conserve resources.
