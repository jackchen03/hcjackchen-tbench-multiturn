Profiling on the new firmware batch shows your /app/solution/recover still misses blocks on some cards and reports partial reports.

Root cause from traces: logger firmware v2 no longer guarantees that each report block starts at a cluster boundary. The old firmware wrote one SDR1 block per cluster aligned to cluster size from the BPB (bytes per sector and sectors per cluster), but v2 can place a valid SDR1 block at any byte offset in the image, not only at cluster-aligned offsets. A scan that steps by cluster size therefore misses valid blocks that survive in the raw image.

Switch /app/solution/recover to scan every byte offset in the image for a valid SDR1 block (magic "SDR1", stream_id, seq, plen, payload, crc32) instead of only cluster-aligned offsets. You already reverse-engineered the block layout in prior steps — reuse that format but drop the cluster alignment assumption. Output must remain payload-only after stripping 4-byte SDR1 header and CRC trailer and verifying CRC, as defined previously — rptverify expects payload-only.

The old cluster-aligned fast path that iterated offsets by cluster size (reading BPB at 0x0B and 0x0D and stepping by cluster_size) must be removed entirely — we will assert its absence. Keep the same interface: /app/solution/recover <input_image> <output_file> must still produce the original report payload bytes (headers/CRC stripped, CRC verified) that pass /app/tools/rptverify, now for both aligned and unaligned images, and must still reproduce /app/recovered.bin from /app/card.img.

This final pivot completes the fat16 cluster chain recovery — byte-wise scan replaces cluster scan and the FAT is still untrusted, but output remains payload-only.
This step must handle range(len(img)) SDR1 scan correctly.
Additionally, write a short JSON report of what you fixed to /workdir/3_pivot-to-unaligned-scan_report.json.
