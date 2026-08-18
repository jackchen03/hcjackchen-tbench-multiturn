That fixed duplicate listings.

But heavy repeat shoppers still see items they already bought. For users with rich history in /app/data/purchases.parquet, the carousel contains products they purchased before. New users look fine because their history is empty.

Extend the same pipeline so that no recommended SKU maps to a product the user already bought. Purchase history uses product-level identifiers, candidate item_id values are SKU-level, so you need /app/data/catalog.parquet with columns sku and product_id to translate. Ensure per held-out user: exactly 20 rows at /app/out/recs.csv with columns user_id,rank,item_id, ranks 1..20, no duplicate item_id after canonicalizing to int, no SKU whose product_id via catalog is in that user's purchased products, ordering stays consistent with current scoring. Do not mutate files under /app/data. Keep the dedup fix from before intact.
