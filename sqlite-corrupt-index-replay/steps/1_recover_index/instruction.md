The dashboard's big-order query errors out with `database disk image is malformed`,
though a full count still shows every order the app reported as saved: the recent
rows are visible through the write-ahead log but are not durable in the main file.
The database at /app/store.db opens, but the checker log at /app/checker.log shows
an integrity complaint naming an index, plus a durable_rows baseline count of rows
already safe in the main file.

Repair the database in place so `PRAGMA integrity_check` returns ok and every
committed order becomes durable in the main file, and so the index-backed big-order
query runs cleanly again. Put your repair in /app/recover.sh so that running
`sh /app/recover.sh /app/store.db` repairs a fresh copy of this same broken state —
a fresh copy means any fixture from this family: the same schema and corruption
pattern with different ids and data, so hardcoding this file's ids fails — and write
/app/recovery_report.json as a JSON object with exactly the keys "rows_recovered"
(integer) and "method" (string). rows_recovered means the final durable order count
minus the durable_rows baseline from checker.log. Also make /app/app.conf
crash-safe: synchronous NORMAL or FULL with automatic checkpointing re-enabled. Keep
the logical schema unchanged — same tables, columns, and index definitions, so
rebuilding index bytes via REINDEX, dump/restore, or VACUUM is expected, but changing
the schema itself fails. More steps follow; conserve resources.
