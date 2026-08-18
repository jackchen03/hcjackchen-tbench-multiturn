# Detect recycled runs via seq-reset

Your previous /app/recover passes checksum and length for unique ids but still lands wrong bytes on some rows. Those rows share the same chunk_id with another live row — chunks for that id sit back-to-back in physical file order and seq restarts at 0 per LOB, so your chain concatenation interleaves two different chained LOBs values into one garbage blob.

Some wide rows are still corrupted due to recycled chunk_id — figure out how to split the physical pool for a given chunk_id. The hint is sequence numbers restarting: chunk_seq == 0 starts a new run. Gather all chunks whose chunk_id matches in physical order, split that sequence into runs at every point where chunk_seq == 0, then select the run whose summed data-byte length equals the on-disk length from the inline pointer (extsize). Don't re-derive the heap.bin or toast.bin layout from scratch — you already have the area and physical order conventions from step1.

Keep the same executable path /app/recover <row_id> and same stdout contract. Your fix for chained LOBs should now handle recycled runs. This step talks about recycled run detection and generation-like reuse detection for chained LOBs — the body must mention expected reused run split logic.
