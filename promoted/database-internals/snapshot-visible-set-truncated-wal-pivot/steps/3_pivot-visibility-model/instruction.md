# Pivot visibility model with wraparound and drop WAL

Further audit found wal.bin was merged from another cluster – its COMMIT and ABORT records are not trustworthy for this dataset. The WAL-reconciled approach you built earlier is now considered wrong for production. Profiling also showed WAL replay at 10x slower than needed on the production trace, so it has to go.

We have a corrected dataset under /app/data_v2/ where clog.bin is now complete (not truncated) and frozen bits are trustworthy after a re-freeze pass. However xids have wrapped around the 32-bit boundary, so simple integer < comparisons give wrong answers for snapshot visibility. The issue only shows up when you compare xid ordering with wraparound.

Data in /app/data_v2/ contains heap.bin, clog.bin, snapshot.bin. Their formats are in /app/FORMATS_V2.md. snapshot.bin gives snapshot xmin, xmax and the in-progress xip list. There is also a dummy wal.bin file in that directory with garbage – your new implementation must not open or read wal.bin at all, tests will verify it is not accessed (strace / file open tracking) and will replace it with random bytes.

Implement a new tool at /app/reconstruct_v2 with usage `/app/reconstruct_v2 <data_dir> <output_file>` that computes the true live row_id set at that snapshot using clog.bin plus frozen bits with wraparound-aware xid ordering (like TransactionIdPrecedes). Drop the WAL-based logic entirely – the new output must differ from the old WAL-based method on wrapped cases, and old approach files must be removed or not consulted.

Write the sorted row_ids one per line into <output_file> with no extra content. We will run on a held-out data_v2 directory with disjoint row_ids and wrapped xids, so make it generic.

Keep literal tokens /app/data_v2/, heap.bin, clog.bin, snapshot.bin, /app/FORMATS_V2.md, /app/reconstruct_v2, wal.bin verbatim. Title keywords pivot, visibility, wraparound and snapshot must appear. Your implementation must assert absence of wal.bin access.
