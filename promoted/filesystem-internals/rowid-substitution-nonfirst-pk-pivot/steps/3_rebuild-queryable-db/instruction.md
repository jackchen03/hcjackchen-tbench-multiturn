The flat files work for manual inspection but investigators can't run queries, joins, or integrity checks on them, and they keep asking for a real database.

Now build a queryable SQLite database from what you've recovered. Create /app/recovered.db (and /workdir/recovered.db if that dir exists) that can be opened with `sqlite3` and passes `PRAGMA integrity_check;`.

It should contain the table defined by the *last* schema you saw (the one in /app/case2/ if present, otherwise /app/case/) with all merged rows inserted preserving exact values — same primary key values, NULLs staying NULL (not empty string), integers exact, text exact including any quotes. After building, `sqlite3 /app/recovered.db "SELECT * FROM <table> ORDER BY <pk>;"` should produce the same logical rows you wrote to merged.txt, and `PRAGMA integrity_check` must return `ok`.

Reuse your existing decoding if needed, but drop the pipe format for this step — the goal is a valid DB file, not text. Keep your earlier artifacts (carve.sh, rows.txt, merged.txt) still working after this step.
