The flat files work for manual inspection but investigators can't run queries, joins, or integrity checks on them, and they keep asking for a real database.

Now build a queryable SQLite database from what you've recovered. Create /app/recovered.db (and /workdir/recovered.db if that dir exists) that can be opened with `sqlite3` and passes `PRAGMA integrity_check;`.

It should contain the table defined by the *last* schema you saw (the one in /app/case2/ if present, otherwise /app/case/) with all merged rows inserted preserving exact values — same primary key values, NULLs staying NULL (not empty string), integers exact, text exact including any quotes.

Common schema / padding / projection rule (carry from Step 2):
- After Step 2, merged.txt already has uniform six-column rows via padding: five-column source rows were padded with NULL at the missing column position (column-name alignment: extra column gets NULL) so that all rows match the six-column canonical schema.
- For this step, use the six-column schema as canonical (the table with more columns, typically the one in /app/case2/schema.sql). Insert all merged rows into that table; for rows where the extra column was padded with NULL, insert NULL, not empty string.
- If last schema is the five-column one (when case2 absent), then merged rows are five-column and no padding needed; but grading will use the six-column case where last schema has six columns, so you must handle padded NULLs.
- This projection ensures `sqlite3 /app/recovered.db "SELECT * FROM <table> ORDER BY <pk>;"` produces the same logical rows you wrote to merged.txt (with NULLs preserved), and `PRAGMA integrity_check` returns `ok`.

Reuse your existing decoding if needed, but drop the pipe format for DB building — the goal is a valid DB file, not text. Keep your earlier artifacts (carve.sh, rows.txt, merged.txt) still working after this step.

Output contract:
- /app/recovered.db (and /workdir/recovered.db) must be sqlite3-openable, integrity_check ok, contains table defined by last schema (six-column when case2 present), with all merged rows inserted using explicit INTEGER PRIMARY KEY values and NULLs preserved via parameter binding.
- Merged rows with padding must be inserted as six-column rows with NULL where missing.
