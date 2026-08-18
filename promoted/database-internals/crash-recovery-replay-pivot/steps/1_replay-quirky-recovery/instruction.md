# Replay quirky recovery

Your team has a page storage engine that recovers after a crash by replaying its write-ahead log. The binary that performed crash recovery was deleted in an incident — only its outputs survive. You have witness pairs from before the loss: each crash site under /app/samples/caseNN contains heap.bin (the heap at crash time, each page with header pageLSN u64 LE, slot_count u16 LE, slot dir {tuple_off u16 LE, flags u16 LE}), wal.bin (flat stream of records {lsn u64, page_no u32, rec_type u8, arg u16, length u16, payload_len u16, payload}), and recovered.bin (the old tool's correct recovered heap that you must match byte-for-byte).

Record bytes layout and type names OVERWRITE, DELTA, SET_SLOT, PRUNE are defined in /app/FORMATS.md, but how each type mutates a page and in what order multiple records apply is not documented — you must infer it by byte-diffing heap.bin against recovered.bin across samples. This is the quirky recovery — its apply semantics are not canonical ARIES.

Build an executable at /app/replay with usage /app/replay <crash-dir> <out-file>. It must read <crash-dir>/heap.bin and <crash-dir>/wal.bin, replay to produce the recovered heap, and write the bytes to <out-file>. Correctness is strict: for every crash site your output must be byte-for-byte identical to recovered.bin. Self-test on /app/samples/ then hidden evaluation uses new sites you haven't seen.

Body includes replay, quirky, recovery, crash, heap.bin, wal.bin, recovered.bin, /app/samples/, /app/FORMATS.md, /app/replay.
