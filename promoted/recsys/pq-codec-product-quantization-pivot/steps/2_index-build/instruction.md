The byte-exact codec for the product quantization store is working and new stores pass validation — that unblocks generation.

Serving still does a full scan over decoded quantized vectors for every query, which is too slow. We need a retrieval index built directly from the exact codec output.

Add /app/pq_index.py with two functions: build_index(store_path, index_path) reads the store at store_path using the codec you already have in /app/pq_codec.py and writes an index file to index_path, and query_topk(index_path, query_vector, k) takes a raw query vector (list of floats) and returns the top-k item ids (list of ints, most similar first) by asymmetric distance against the quantized vectors.

The index must rely on the precise vectors returned by your codec — not on raw sample files or re-invented codebooks. Use /app/queries.jsonl as a small sample workload to sanity-check, but grading will use held-out stores and unseen queries, so the index has to work for any store that your codec can handle.
