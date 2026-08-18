The factors now reconstruct correctly and the head band no longer retrieves unrelated products.

Our offline audit still needs visibility into which items received the extra correction. Extend /app/factorstore.py with a helper get_head_flags(ckpt_dir) that returns a boolean array (or list) of length num_items indicating which items are head items. It should parse the same checkpoint data you fixed in the previous step, not hardcode ids, and work on unseen checkpoints with the same layout.

Also generate a validation artifact at /app/ckpt/head_diagnostics.json containing at minimum head_count and head_ids (sorted ascending). The file should be valid JSON and reflect the true head set from the checkpoint's residual side data.

Keep load_item_factors working as before — it must still return the correct (num_items, factor_dim) float32 matrix.
