The byte-matched CDC stream we just built is now used for recovery validation. Upstream produces a checkpoint snapshot expectation for each physical WAL segment.

Add a verification tool at /app/verify with usage /app/verify <wal_segment_path> <checkpoint_path> <report_path>. Checkpoint format is defined in /app/CHECKPOINT_FORMAT.md, and the report JSON you must write is defined there as well: it goes to /app/recovery_report.json path given as third argument when invoked as /app/verify <wal_segment_path> <checkpoint_path> <report_path>.

Your verify tool must replay the WAL segment using the exact same anti-canonical dialect you reverse-engineered for /app/decode — same ordering keyed on begin-order counter, same page-header-skip stitching, same toast reloid filtering and little-endian chunk reassembly, same subtransaction abort filtering — to compute final table state and compare against /app/checkpoint.json. If your replay logic is canonical or off by endianness, row_count and hash will mismatch even though single rows looked fine.

Samples for this step are under /app/checkpoint_samples/ with matching expected reports. You already know the area and container conventions from /app/FORMAT.md and your previous /app/decode binary — do not re-derive them, keep your existing decoding path and reuse it.

Do not implement logical WAL handling yet — that belongs to a later migration step.