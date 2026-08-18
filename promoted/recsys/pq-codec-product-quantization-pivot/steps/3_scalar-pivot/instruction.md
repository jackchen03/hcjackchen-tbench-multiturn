The product quantization index you built helps, but profiling traces we just collected shows the variable-bitrate contiguous bitstream unpacking dominates tail latency — per-query L2 over PQ codes is slower than expected and the old format's centroid tables don't fit in cache.

We are dropping product quantization entirely and moving to per-dimension 8-bit scalar quantization for serving speed.

Update /app/pq_codec.py so that decode_store(path) and encode_store(vectors, out_path) now handle only the new format with magic "ISQ1": header is 4-byte magic "ISQ1", u32 LE dim, u32 LE num_vectors, float32 LE per-dim min array, float32 LE per-dim max array, then num_vectors * dim uint8 codes row-major, then u32 LE crc32 over everything before crc. Encode computes per-dimension min/max across the input batch and linearly quantizes each value to uint8. Old "IPQ1" stores must no longer decode — they should raise or be treated as invalid.

Remove all product-quantization-specific packing, centroid table, and variable-width bitstream logic, and delete /app/pq_index.py since the scalar path does a direct scan without a prebuilt index. Files that talk to the old format should fail /app/pq_validate (which now validates only "ISQ1").
