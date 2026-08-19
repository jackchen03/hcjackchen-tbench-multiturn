We are building a Postgres-like storage engine CDC. It decodes physical WAL segments into a logical change stream: heap modifications become ordered INSERT / UPDATE / DELETE records with fully materialized column values. We previously relied on a third-party binary /app/wal2logical as ground truth. Its license is expiring and it must be replaced.

Our in-house decoder produces a stream that diffs from the baseline everywhere: change order is off, rows from uncommitted transactions appear, and wide columns are garbled unreadable. Eyeballing single records looks okay, but byte diff fails.

Write an executable at /app/decode with usage /app/decode <wal_segment_file> <output_file>. It reads a physical WAL segment file and writes the logical change stream to the output file. Grading is strict byte-for-byte equality against /app/wal2logical output for the same input segment — not a single byte may differ.

The on-disk byte layout of the physical WAL segment (pages, page headers, record framing) and the container format of the logical output stream (fields per logical record) are documented in /app/FORMAT.md — follow it for outer container. You can self-test with samples under /app/samples/ : each sample segment has a matching baseline output from /app/wal2logical.

Crucially, FORMAT.md does not fully specify which changes enter the stream, in what order they are emitted, or how wide column values are reassembled. Those semantics are opaque — you must craft inputs, run /app/wal2logical repeatedly, and byte-diff its output (od -c, hexdump) to reverse-engineer the exact dialect. Textbook logical decoding will fail.

Your binary must be fully self-contained at grading time: /app/wal2logical will be removed, so you cannot shell out to it or depend on it at runtime. Do not hardcode sample outputs — grading uses held-out WAL segments you have never seen with disjoint xids, reloids, and value ranges. The physical WAL reimpl anti-canonical dialect requires probing: commit vs begin order, page-boundary stitching with asymmetric headers, toast filtering and little-endian chunk sequence, and subtransaction visibility.

More steps follow after this; conserve resources and do not create files for later steps yet.