Serving profiled the restored checkpoint path — loading the flat .npy files dominates p99 latency because the whole user and item matrices are read into memory at once. That restored flat layout we built in step 1 is too large to ship to edge.

Switch to a memory-mappable serving layout that can be mmap'd directly and drop the flat files. Write the serving blob to /app/out/serving/model.mmap as raw float32 LE factor rows contiguous, and a JSON sidecar at /app/out/serving/layout.json that tells serving how to find a factor (must include keys: dim, num_users, num_items, user_offset, item_offset, dtype). The dot product of user u and item i using this mmap layout must match the scores from the restored factors for all held-out pairs.

When this pivot is done, the old flat files /app/out/P.npy and /app/out/Q.npy must be removed — serving will only use the mmap bundle.
