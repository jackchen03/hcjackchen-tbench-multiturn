Profiling on larger traces from the same archiver shows the current decoder is too slow and memory heavy. Allocating a full bytearray of i_size and linearly scanning extents to copy each block dominates for files with thousands of extents and deep trees (eh_depth>0). Lookups dominate and memory spikes.

We need to pivot the extractor implementation for this noncanonical ext4 decode workload:

Rewrite /app/myextract to use streaming output and binary search over pre-resolved absolute extents:
- Pre-resolve all leaf extents to absolute logical offsets once (using the delta decoding you already discovered).
- Sort them by logical_block and build a searchable index; use binary search to service output ranges.
- Write directly to stdout in logical order without allocating a full file-sized bytearray. Gaps and unwritten ranges must still stream as zeros.
- Keep behavior byte-identical to the reference extractor on all images.

Also drop the audit report work we added: after this step /app/extent_report.json must NOT exist (delete it if present). The report duplicated work and is no longer required for the streaming pivot. Absence will be checked.

Motivation: sorted array plus full allocation too slow on traces we just profiled — switch to streaming with binary search and drop ordering/report work we added. Old approach of full allocation and separate report generation must be removed; new code must not contain report generation.

Keep CLI identical: myextract <image path> <inode> to stdout. Byte-exactness still pinned. Remove any code that writes /app/extent_report.json.
