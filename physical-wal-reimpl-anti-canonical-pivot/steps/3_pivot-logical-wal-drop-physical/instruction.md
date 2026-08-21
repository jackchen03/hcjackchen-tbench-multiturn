Profiling from the last step showed the physical WAL path is a bottleneck: page-boundary record stitching that skips asymmetric LONG vs SHORT page headers, TOAST chunk reassembly with little-endian chunk sequence, begin-order sorting, and subtransaction assignment rollup are expensive and brittle under the new high-throughput workload. Upstream now emits logical WAL directly.

See /app/MIGRATION.md and the new input format in /app/LOGICAL_FORMAT.md. There is a reference decoder /app/logical2stream that decodes logical WAL segments into the same logical change stream container defined in /app/FORMAT.md output section — use it for probing.

Rewrite /app/decode so it decodes logical WAL segments (format per /app/LOGICAL_FORMAT.md) into the byte-exact logical change stream container. Usage stays /app/decode <logical_wal_segment_file> <output_file>. You no longer need to handle physical WAL files.

Crucially, this is a pivot: drop the physical path entirely. Your new /app/decode must NOT contain physical WAL handling — no LONG header / SHORT header page stitching, no TOAST reloid filtering or chunk_seq little-endian reassembly, no begin_seq ordering, no XACT assignment subtransaction rollup. Those code paths must be absent, not just unused. Keep only logical WAL decoding. The output container remains per /app/FORMAT.md — same rec_len, op, topxid, ncols, col_len/col_bytes as before.

Samples are in /app/logical_samples/. Grading feeds held-out logical WAL segments with disjoint values and byte-diffs your output against /app/logical2stream golden, and asserts physical handling absence.

This completes the physical-wal-reimpl anti-canonical pivot to logical.
This step must handle pivot-logical correctly.
