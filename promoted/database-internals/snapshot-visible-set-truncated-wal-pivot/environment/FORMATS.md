heap.bin is JSON rows with row_id, xmin, xmax, and frozen. clog.bin is a JSON xid-status map and may be truncated. wal.bin is JSON records carrying xid and COMMIT or ABORT. queries.bin is JSON inclusive [low,high] pairs.

