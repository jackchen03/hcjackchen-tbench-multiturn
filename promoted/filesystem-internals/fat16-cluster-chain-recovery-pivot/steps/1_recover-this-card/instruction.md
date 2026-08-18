We have a batch of old data logger cards. Each card is a FAT16 image, and the file system looks completely fine at first glance.

The card image at /app/card.img holds an instrument report file written by the logger. Our export tool copies the report by the size recorded in the directory entry — the copy finishes with no error and the output size exactly matches the directory record. But when we feed that copied file to the integrity checker at /app/tools/rptverify, it reports the file as corrupted. rptverify exits with 0 for a good file and non-zero for a bad file.

We need the true original bytes of that report, as it was when first written to the card.

Recover it to /app/recovered.bin. It is correct only if two conditions hold: it passes /app/tools/rptverify (exit 0), and it is byte-for-byte identical to the report's original content at write time.

This is a fat16 cluster chain recovery problem — the FAT chain is suspect, clusters appear free or cross-linked, and a size-correct copy still fails verification. The real bytes are still somewhere in the image.

More steps follow, conserve your work for generalization.
