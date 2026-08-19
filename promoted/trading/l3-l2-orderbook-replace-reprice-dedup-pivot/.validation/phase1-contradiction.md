# Phase-1 REPLACE duplication and undefined REPRICE contract

Phase 2 stopped before bundle construction for two independent specification defects.

## Step 1 duplicates Step 2

Step 1 explicitly defines the `R|seq|old_order_id|new_order_id|new_price|new_size` record and requires `/app/rebuild.py` to correctly rebuild L2 for *any feed of the same format*. Correct handling necessarily removes the old order and installs the new order once. Step 2 then reports that REPLACE is still double counted and asks for exactly that same behavior. A correct Step-1 implementation therefore already satisfies Step 2; forcing Step 1 to remain wrong creates an unfair hidden boundary.

## Step 3 has no gradeable REPRICE wire or priority contract

The only feed records defined in Step 1 and the environment are `A`, `X`, `E`, `T`, and `R` (REPLACE with old and new order IDs). Step 3 introduces a distinct `REPRICE` operation but never defines its event code, field layout, or whether it is encoded as `R` with identical IDs. Worker-fanout duplicates likewise have no delivery identifier or deduplication/fencing key beyond an unspecified narrative.

The declared output contains only aggregated L2 price/quantity levels. It does not expose per-order queue ordering, original priority sequence, or an internal state artifact, so two implementations with opposite price-time priority behavior can produce identical required JSON. The dossier suggests hidden inspection of an internal map or `/app/book_state.json`, but neither instruction defines such an artifact, and the environment says not to invent alternative outputs.

Phase 1 must narrow Step 1 so REPLACE remains a genuine Step-2 addition, then define a concrete REPRICE wire record, duplicate-delivery identity/fencing semantics, and a model-visible output or artifact that makes preserved priority observable and gradeable.
