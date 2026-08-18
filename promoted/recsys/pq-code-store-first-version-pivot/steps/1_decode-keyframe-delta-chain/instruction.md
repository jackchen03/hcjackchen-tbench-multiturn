# Decode the PQ code store — first vector per block correct, rest drifts

Your offline recall uses product-quantized item vectors. Each item is compressed to M subquantizer codes (uint8, 0-255). The batch of codes is stored in a custom binary store file we call a pqs file. Something is wrong: with the current decoder in /app/pq_codec.py every block's first item decodes perfectly against ground truth, but every later item in the same block is garbage and the error gets worse toward the block end, then the next block's first item is suddenly correct again.

The sample stores are under /app/store/ (sample_000.pqs etc). Next to them /app/store/codes_sample.npy is the already-decoded correct codes for those samples — a numpy array shape (num_items, M) dtype uint8 you can compare against. The validator program is /app/pq_store_validate — pass a store path and it returns 0 if the file structure is legal, non-zero otherwise. The buggy codec is in /app/pq_codec.py.

Fix decode_store(path) in that file. It takes a store file path and must return all codes in the store as a numpy array shape (num_items, M) dtype uint8 in the same order the writer used. For the sample stores its output must be exactly equal to codes_sample.npy.

Don't modify /app/pq_store_validate or any file under /app/store/. Only deliver /app/pq_codec.py. The title talks about pq code store first version — you must make the first vector pivot correct and stop the intra-block drift. More steps follow; conserve resources.
