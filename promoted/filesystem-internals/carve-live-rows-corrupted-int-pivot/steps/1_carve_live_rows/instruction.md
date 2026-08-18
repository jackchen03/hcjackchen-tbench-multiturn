We have a production SQLite file that was rescued to `/app/broken.sqlite`. It contains a single business table `T(id INTEGER PRIMARY KEY, name TEXT, val INTEGER)`. The file is now unreadable: opening with sqlite3 fails with `file is not a database` or `database disk image is malformed`, so normal `SELECT * FROM T` does not work.

Our audit counter records the exact number of live rows `T` should contain, but naive recovery gives wrong counts. If we force the file open and dump whatever is walkable, the count comes out noticeably low, like an entire range disappeared. If we carve every byte sequence that looks like a data row, the count overshoots and mixes in rows that should not belong to `T` with mismatched field values.

We need the true current live rows of `T` — not one missing, not one extra, and every field exactly matching the original values.

Write a repeatable recovery script `/app/recover.sh` that receives two args: first is input SQLite image path, second is output database path. After running, output path must be a normally openable SQLite database containing one table named `T` with the same schema `T(id INTEGER PRIMARY KEY, name TEXT, val INTEGER)` and only the complete set of valid live rows.

First run it on `/app/broken.sqlite` to create `/app/recovered.sqlite`. Later validation will run your `/app/recover.sh` on another image of the same corruption type but with different content, so do not hardcode any row counts, primary key ranges, or field value patterns from this file — the script must be generic.
