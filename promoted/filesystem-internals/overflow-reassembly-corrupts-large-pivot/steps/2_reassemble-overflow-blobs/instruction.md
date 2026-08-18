You now have an inventory of rows and declared lengths from the corrupted file.

The inventory looked right, but the actual bytes are tricky. When we tried a textbook SQLite overflow carver, the short rows came out perfect and the row count matched, yet the large rows were silently wrong — same declared length in the record header, but the assembled bytes didn't match the original. The application had checksummed every BLOB, and byte-for-byte comparison fails on those large ones. The corruption is invisible from row counts or short fields.

Now recover every row's BLOB byte-exact, no encoding or padding changes.

- Write each recovered BLOB to /app/recovered/ — one file per row, filename is `<rowid>.bin` (e.g. `42.bin`). File content must be the original BLOB bytes exactly.
- Also make your logic reusable: create /app/recover.sh that takes two arguments: first is a SQLite image path, second is an output directory. When run, it must write all rows from that image into the output dir using the same `<rowid>.bin` naming rule. We will re-run it on other images of the same family to verify generality.

Do not assume the header's reserved-byte field is correct. The file's first page is wiped so `sqlite3` never opens regardless of what you put there — you must infer structure purely from raw pages and chain consistency.

You already know the file is at /app/broken.sqlite and how its b-tree leaves are laid out from last step; build on that.
