# Recover committed set from recycled WAL

We have a Postgres-like storage engine that writes transaction logs sequentially into log segment files inside blocks, and replays them after a crash to recover data. Last week the machine lost power while writing logs. After reboot the recovery tool ran normally, tables read fine, logs reported no checksum errors. But reconciliation is red: the recovered table has extra rows, and the tool reported a batch of committed transaction IDs that were never started in this run before the crash.

Looking at logs blind shows nothing obviously broken. A log segment is regularly structured binary, you can walk it block by block, record by record, with od and hexdump it looks fine, each record's checksum passes, and the current buggy recovery tool just reads to EOF and counts every commit it sees, which produces the over-counted result that is currently live.

The crash site is archived under /app/data/, engine's segment files. Byte layout is in /app/FORMATS.md: block header and record header including per-record checksum and back-link field pointing to previous record position, plus record types (begin, write, commit, abort, checkpoint) are documented there. The environment also keeps the current buggy recovery tool binary at /app/replay_naive, usage /app/replay_naive <dataDir> <outputFile> — you can use it to reproduce the over-count phenomenon and observe its behavior on self-constructed inputs.

Write an executable program at /app/recover with usage /app/recover <dataDir> <outputFile>: read log segment files from <dataDir>, compute the true set of transaction IDs that successfully committed before the crash, and write those IDs sorted ascending decimal, one per line, newline terminated, no header or extra content in <outputFile>. We will later run your program on a different crash site with different IDs and segment content, so make it correct for any format-compliant site, not just current sample.

Title keywords must include recycled, wal, committed, set, and mention recover and FORMAT.

Output contract: /app/recover exists, executable, reads /app/data/ style directory, byte layout per /app/FORMATS.md, writes <outputFile> with decimal IDs sorted ascending one per line \n terminated exactly as verifier asserts.
