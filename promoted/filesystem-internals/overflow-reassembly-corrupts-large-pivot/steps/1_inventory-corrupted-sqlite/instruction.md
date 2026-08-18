We rescued a SQLite file from a failing disk, now at /app/broken.sqlite. It should contain an archive table with an integer primary key and a large BLOB column, but it won't open: any use of `sqlite3` to query it reports `database disk image is malformed`.

Your first job is to figure out what's actually inside without relying on `sqlite3`.

Scan the raw file, locate the table b-tree leaf pages, and for each row present extract the integer primary key and the declared payload length of the BLOB as stored in the record header. Do not attempt to reassemble overflow yet, just report what the cell says it should be.

Write two files:

- /app/inventory.json — a JSON object mapping each row id (as a string, e.g. "42") to its declared BLOB payload length (integer, number of bytes the record header says the BLOB should have).
- /app/page_info.json — a JSON object with at least `{"page_size": <int>}` where page_size is the file's page size from the header at offset 16.

Both files must be valid JSON. The inventory must include every row you can find in the docs table b-tree; rowids must be exact.

More steps will follow that build on what you found here, so conserve the parsing logic you develop. Do not create any other output yet.
