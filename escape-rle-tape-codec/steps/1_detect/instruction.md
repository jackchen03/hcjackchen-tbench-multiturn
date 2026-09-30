The tape output of /opt/ref/bin/tape_encode on /data/tapes/long_200x41.bin and the short controls looks surprising next to naive expectations for run counts, length bytes, and total sizes from wc -c.

Run /opt/ref/bin/tape_encode on each of /data/tapes/long_200x41.bin, /data/tapes/short_5x42.bin, and /data/tapes/short_hello.bin, inspect every output with od -A d -t x1 and wc -c, and write /app/report_S1.md with exactly one TABLE block per input tape.
Each block opens with TABLE <path>, then one RUN <HEX> LEN <n> line per token chunk in tape order, one TRAILER <off> CHK <hex> line per trailer byte in tape order, then SIZE <n> with the wc -c total, and closes with END TABLE.
HEX and hex are uppercase two-digit bytes, offsets are decimal byte positions, and blank lines are ignored. Blocks may appear in any order. Measure the split cap L on the first long run and record it once outside any block as SPLITCAP <n>.

Grading checks this report against the same solve-time tapes listed above; only /app/report_S1.md counts in this step.
