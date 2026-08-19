# De-masked pivot — decompress splice

Your run-split fix from last step clears uncompressed shared-id rows but still fails compressed rows and some second-run rows. Fresh evidence: reading extsize with PG canonical mask 0x3FFFFFFF over-reads the boundary by up to +2^29 — the inline pointer's len_word packs compression method in bits 30..29 and extsize is only 29 bits, not 30. PG recall is a liability here.

The heap inline pointer len_word is packed: bit31 reserved zero, bits 30..29 cmethod (2-bit compression-method selector), bits 28..0 extsize (29-bit on-disk chunk-data byte count). Correct decode is cmethod = (len_word >> 29) & 0x3, extsize = len_word & 0x1FFFFFFF. The old mask 0x3FFFFFFF leaves method bits polluting extsize, yielding boundary way too large and making demasked pivot impossible, plus it breaks decompression because inverse must consume exactly extsize bytes.

Switch to de-masked pivot. For any row, de-mask len_word to get true extsize and cmethod, then select the run whose summed data_len == de-masked extsize (not the PG-masked value). If cmethod==0 output the run bytes as is. If cmethod==1 apply the documented reversible transform from FORMAT.md (method-1 LZSS-style inverse) consuming exactly extsize compressed bytes to produce exactly rawsize decompressed bytes, and splice at len boundary not current chunk len.

Remove the old PG mask logic that used 0x3FFFFFFF. The previous path that masked extsize with 0x3FFFFFFF must go — it is wrong and must not be present in final /app/recover. Keep same command /app/recover <row_id> and same stdout contract. Read FORMAT.md for heap.bin, toast.bin, method-1 layout. You need de-masked extsize, demasked pivot, chained lobs, pivot, and byte-exact splice with cmethod, extsize, rawsize, 0x1FFFFFFF all together.

Write a short JSON report of demasked handling to /app/3_demasked_report.json containing at least counts of cmethod=0 vs cmethod=1 rows handled and that you used mask 0x1FFFFFFF. This final recover must produce byte-exact LOBs for all rows, including compressed second-run shared-id chained LOBs.

The output for this step must include /app/3_demasked_report.json. Also keep /app/2_recycled_report.json from previous step intact for regression.
