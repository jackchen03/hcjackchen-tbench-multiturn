# Recover chained LOBs — chain walk

We have a tiny document store that spills wide body fields into an overflow file. The main heap file and the overflow chunks live under /app. The on-disk layout for heap.bin and toast.bin is described in /app/FORMAT.md. A few rows have their true original body bytes shipped under /app/samples as <row_id>.bin you can use to see the symptom — most rows look fine but some wide rows read back with a truncated or garbage tail even though no error is raised.

Build an executable at /app/recover that takes a single argument row_id (e.g. /app/recover 1003) and writes that row's body original bytes exactly to stdout, no extra newline or wrapper. At this stage just walk the chained LOBs in physical file order and follow FORMAT.md for heap and overflow layout. The file naming <row_id>.bin in samples is just for reference.

Your binary must read heap.bin and toast.bin under /app and implement the chain walk for chained LOBs recovery. The title keywords recover and chain and chained and lobs must appear but the fix at this stage is just walking the chain — output must be /app/recover.
