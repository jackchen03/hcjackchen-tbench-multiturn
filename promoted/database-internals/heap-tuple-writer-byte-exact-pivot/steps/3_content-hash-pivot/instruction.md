# Content-hash pivot replacing global overflow valueid

Your byte-exact encoder from last step matches legacy_writer, but production tracing shows the global valueid counter starting at 1000 makes restore non-deterministic across shards — same row content gets different overflow pointers depending on which shard overflowed first. The counter also leaks ordering.

Switch the overflow pointer's valueid field to be content-addressed and remove the global counter state entirely. For every overflowed text value, compute FNV-1a 32-bit hash of the raw bytes (offset basis 2166136261, prime 16777619, mod 2^32) and use its low 32 bits as valueid. Keep rawsize, extsize, toastrelid=0x0BADF00D, and the 0x01,0x12 marker bytes as before. Do not keep a global counter incrementing across rows.

Also emit a spill manifest at /app/overflow_manifest.json. It is a JSON object {"spills":[{"row":<row_index>,"col":<col_index>,"valueid":<hash>,"len":<len>},...]} listing each overflowed value in row order then column order, where valueid is the FNV-1a hash you emitted and len is the raw length.

The old path that maintained a mutable counter starting at 1000 across rows must be gone — final /app/encoder must not contain that counter logic. Motivation is deterministic replay, so absence of global counter is required.

Keep the same stdin JSON input and same stdout binary tuple stream format with 2-byte LE length, keep /app/encoder at same path, keep probing support via /verifier/legacy_writer for layout but valueid semantics changed. Overflow decision of largest-first by inline size until total_size <= 140 and tie by lowest column index still applies.

This step is a pivot from counter-based to hash-based overflow valueid plus manifest.

Title keywords heap, tuple, writer, overflow must still appear alongside hash pivot.
