That set approach OOMs on billion-scale backfill – nightly audit gets killed. Sorted array too slow on the traces we just profiled. We need to pivot.

Extend /app/seen_reader.py to add iter_served_items(path) that yields item ids in strictly ascending sorted order without materializing the whole set at once. It must decode using the same on-disk format you already recovered, but as a generator. The audit path is not allowed to call read_served_items internally; it has to use the streaming iterator.

Also add an audit CLI to the same module so we can run:

python3 /app/seen_reader.py --audit --served <served.bin> --candidates <candidates.txt> --out <unserved.txt>

where candidates.txt is a text file with one item id per line (sorted), served is a bitmap file, and out should contain only those candidate ids not in the served set, one per line sorted ascending. Implement the audit using iter_served_items with a sort-merge, not by loading the full served set via read_served_items.

Keep read_served_items and write_served_items working – previous steps still need to pass – but the new code path must not rely on the old set-materializing behavior for iteration or audit.
