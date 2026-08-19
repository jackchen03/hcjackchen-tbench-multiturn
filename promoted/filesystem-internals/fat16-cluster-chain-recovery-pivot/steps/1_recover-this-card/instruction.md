We have a batch of old data logger cards. Each card is a FAT16 image, and the file system looks completely fine at first glance.

The card image at /app/card.img holds an instrument report file written by the logger. Our export tool copies the report by the size recorded in the directory entry — the copy finishes with no error and the output size exactly matches the directory record. But when we feed that copied file to the integrity checker at /app/tools/rptverify, it reports the file as corrupted. rptverify exits with 0 for a good file and non-zero for a bad file.

We need the true original bytes of that report, as it was when first written to the card.

Format clarification (fixes payload-only vs header/trailer confusion):
- The raw instrument blocks on the card have SDR1 framing: 4-byte magic "SDR1", then stream_id u32 LE, seq u32 LE, plen u16 LE (payload length for this block), followed by payload bytes, followed by a CRC trailer (4-byte IEEE CRC32 of preceding header+payload, or 2-byte truncated in v1 firmware docs). The logger wrote one SDR1 block per cluster on v1, but payload length varies for last block.
- The true report file is NOT the raw cluster dumps with headers and CRCs inside. It is payload-only: concatenation of payload[:plen] ordered by seq 0..N-1, with all SDR1 headers and CRC trailers stripped, and each block's CRC verified before inclusion. Any output that still contains SDR1 headers or CRC trailers is WRONG.
- `rptverify` is defined to expect payload-only output: it reconstructs expected seq continuity and content hashes from the payload stream, and exits 0 only if the payload-only file is byte-exact to original report and its underlying blocks would have had valid CRCs. It does NOT expect headers/CRC bytes to be present in the output file — it expects them to have been removed and verified.

Recover the payload-only report to /app/recovered.bin. It is correct only if two conditions hold: it passes /app/tools/rptverify (exit 0, which checks payload-only), and it is byte-for-byte identical to the report's original payload content at write time (headers/CRC stripped).

This is a fat16 cluster chain recovery problem — the FAT chain is suspect, clusters appear free or cross-linked, and a size-correct copy still fails verification. The real payload blocks are still somewhere in the image, but must be found by scanning for valid SDR1 magic + CRC, not by trusting FAT.

More steps follow, conserve your work for generalization.
