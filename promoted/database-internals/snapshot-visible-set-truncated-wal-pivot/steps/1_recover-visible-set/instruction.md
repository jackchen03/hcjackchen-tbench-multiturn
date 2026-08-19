# Recover snapshot visible set from truncated CLOG

We have a Postgres-like heap storage engine that recently crashed and recovered. After recovery the heap was archived and we want a report snapshot listing the rows that are truly live at the latest snapshot point. The current report is clearly wrong: it includes rows that were never committed and drops rows that were committed.

What's tricky is that if you inspect the problematic tuples with pg_inspect they look perfectly clean — either marked frozen and all-visible or marked with clean committed state, and catting or hexdumping them shows nothing wrong. The existing reporting script just follows the tuple header flags plus the commit status directory to decide visibility, but the result is wrong in both directions.

Data lives in /app/data/ with three binary files: heap.bin (heap pages with tuples), clog.bin (commit status directory), wal.bin (log stream from before the crash). Their byte layout is in /app/FORMATS.md and you can also look at pg_inspect.py for parsing. report_buggy.py shows the current wrong reporter establishing the red symptom.

Write an executable at /app/reconstruct with usage `/app/reconstruct <data_dir> <output_file>`. It should read heap.bin, clog.bin, wal.bin from <data_dir>, compute the set of row_ids that are truly visible (alive) at the latest snapshot, and write those row_ids as decimal sorted ascending one per line into <output_file> with no extra content. We will run your program on a different data directory with disjoint row_ids, so make it work for any input matching the format, not just the sample in /app/data/.

Keep the literal tokens /app/data/, heap.bin, clog.bin, wal.bin, /app/FORMATS.md, /app/reconstruct, /app/pg_inspect.py verbatim. The title keywords snapshot, visible set, truncated and WAL must appear in your reasoning but the task symptom is that the report includes uncommitted and misses committed rows despite looking clean under pg_inspect.

More steps will follow; conserve resources.