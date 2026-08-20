# Commit index formats

Sorted step-2 `CIDX`: 16-byte big-endian header (`0x43494458`, version 1, entry count, CRC32 of first 12 bytes), followed by sorted `(xid u64, commit_lsn u64)` entries.

Hash step-3 `CIDY`: 24-byte header (`0x43494459`, version 2, 64 buckets, entry count, buckets offset 24, entries offset 280), then 64 big-endian u32 heads and 24-byte entries `(xid u64, commit_lsn u64, next_index u32, reserved u32)`. Empty/tail is `0xFFFFFFFF`; entries are inserted in ascending-xid order using head insertion.
