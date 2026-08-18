Your previous recovery to /app/recovered.bin worked for this card. Now we need it to work across the whole batch.

Build an executable at /app/solution/recover that takes two arguments: first is the input image file path, second is the output file path, and recovers that image's report to the specified output path. The same fat16 cluster chain recovery must now be reusable — we will run it directly on other images from the same batch with different report sizes, different stream_id, different divergence cluster, and different FAT layout, so do not hardcode any result that only holds for /app/card.img.

Keep /app/recovered.bin intact; your new binary should be able to reproduce it when run as /app/solution/recover /app/card.img /app/recovered.bin, and any output it produces must still pass /app/tools/rptverify.

Only intrinsic content of the report blocks, not the FAT chain, can be trusted for recovery. The tool must discover the valid blocks in the raw image and reassemble them in the right order.

A further firmware change is coming, so conserve resources and keep the binary modular.
