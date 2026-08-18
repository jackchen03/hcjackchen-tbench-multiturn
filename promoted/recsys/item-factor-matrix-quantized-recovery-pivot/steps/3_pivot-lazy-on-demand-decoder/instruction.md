Load tests with a 10x larger catalog OOM when we materialize the full dense (num_items, factor_dim) matrix upfront via load_item_factors. Traces show lookups dominate and we rarely need all factors at once. The eager full-matrix precomputation we added is now too slow and memory-heavy.

Switch to a lazy on-demand decoder. Implement in /app/factorstore.py a class QuantizedItemStore that preloads only codebooks and compact codes in __init__(ckpt_dir) and provides per-item access:

- get_item_factor(item_id: int) -> np.ndarray shape (factor_dim,) float32
- get_batch_factors(item_ids: List[int]) -> np.ndarray shape (len(item_ids), factor_dim) float32

Both must return the same correct factors as before (including the head correction) for any item. For backwards compatibility keep load_item_factors(ckpt_dir) but reimplement it as a thin wrapper that internally uses the lazy store's batch path, not as a separate dense construction duplicating all logic.

Drop the old eager full-matrix allocation: __init__ must not allocate a (num_items, factor_dim) float32 array upfront, and the main decode path should not build the entire dense matrix unless explicitly asked via the wrapper. The previous approach of allocating a full dense array in the constructor or in get_item_factor should be removed.

get_head_flags and /app/ckpt/head_diagnostics.json from the prior step should continue to work.
