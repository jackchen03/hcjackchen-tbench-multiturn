Product QA reviewed the fixed carousel for repeat shoppers and found a new pattern: the same product still shows up twice via different SKU variants — different pack sizes share one product_id but have distinct item_id SKUs. Users who already bought a lot still feel the list is repetitive, and the dedup you added only catches identical item_id.

We need to pivot the deduplication. The sorted dedup on item_id alone is too narrow for repeat shoppers who own many products. Switch to product-level diversity: at most one SKU per product_id per user. Use /app/data/catalog.parquet with columns sku and product_id to group candidates by product, keep the first SKU per product in current scoring order, then take top 20.

That means the old SKU-only drop_duplicates on item_id work should be dropped — the list must not contain duplicate product_id values via catalog, not just duplicate item_id. Keep the already-bought exclusion you added, keep exactly 20 rows per user at /app/out/recs.csv with columns user_id,rank,item_id ranks 1..20 contiguous, scoring order preserved, no SKU whose product_id is already bought.

Also emit /app/out/diversity.json with per-user counts of duplicate products (all zero after fix). Do not mutate files under /app/data. Ensure repeat shoppers see no already bought items and no dup products after the pivot.
