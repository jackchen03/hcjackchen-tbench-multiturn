Your baseline /app/mymkfs from the last step still mismatches on STRIDE>1 images. The reference marks alignment gaps as used and its free-space counters drop when stride is >1, so the superblock and GDT bytes differ.

Extend the same /app/mymkfs binary you already have to handle STRIDE>1. The three metadata segments that are clustered per flex should each start on an absolute block multiple of stride, the alignment pad blocks zero-filled and marked used in the owning bitmap, with free counts reconciled accordingly.

When you have stride handling working for cases where each flex index is divisible by stride, write the number of pad blocks you observed for the probe spec 16 MiB stride 2 flex 4 into /app/stride_audit.json as JSON like `{"spec": "16-2-4", "pad_blocks": <int>}`. That file is what we will check for this step.
