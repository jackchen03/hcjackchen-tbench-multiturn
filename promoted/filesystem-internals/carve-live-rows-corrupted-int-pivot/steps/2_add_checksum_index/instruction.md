Now that the table is recovered to `/app/recovered.sqlite`, auditors need secondary verification that the recovered set is exactly the live set.

Build a checksum index on top of the previously recovered artifact.

Write `/app/build_index.sh` that takes two args: first is recovered SQLite path (e.g. `/app/recovered.sqlite`), second is output index SQLite path. When run on `/app/recovered.sqlite` it must create `/app/recovered_index.sqlite` containing:

- table `T_checksum(id INTEGER PRIMARY KEY, name TEXT, val INTEGER, checksum TEXT)` with the same rows as `T` plus a column `checksum` which is the hex-encoded SHA256 of name concatenated with stringified val (`name + str(val)` UTF-8).
- index `idx_T_val` on `T_checksum(val)`.

The checksum table must reference only the exact live rows you carried from the previous step — no ghost rows mixed in. First run it to produce `/app/recovered_index.sqlite` from `/app/recovered.sqlite`.
