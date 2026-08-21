Production traces just profiled show the SQLite B-tree approach that relied on INTEGER PRIMARY KEY varint decoding is too slow — varint parsing dominates lookups. The legacy integer handling that caused the earlier misinterpretation keeps triggering, and downstream archive no longer uses SQLite.

Switch the archive format to a flat binary with explicit 64-bit little-endian encoding and drop the old SQLite varint handling.

Write `/app/encode.sh` that takes two args: first is verified SQLite path (either `/app/recovered.sqlite` or `/app/recovered_index.sqlite`), second is output binary path. When run on `/app/recovered_index.sqlite` it must produce `/app/recovered.bin` in this exact format:

- 4 bytes ASCII magic `LR01`
- 4-byte little-endian unsigned int count N
- N records sorted by id ascending, each: id 8-byte LE signed, name_len 2-byte LE unsigned, name bytes UTF-8, val 8-byte LE signed, checksum 32-byte raw SHA256 of name bytes + str(val) bytes

Absence requirements: `/app/recovered.bin` must NOT start with `SQLite format 3\0`, must NOT be openable as SQLite via `sqlite3`, and `/app/encode.sh` must drop the old SQLite recovery approach — it must NOT call `sqlite3 <input> .recover`.

First run it on `/app/recovered_index.sqlite` to create `/app/recovered.bin` (fallback to `/app/recovered.sqlite` if needed).
