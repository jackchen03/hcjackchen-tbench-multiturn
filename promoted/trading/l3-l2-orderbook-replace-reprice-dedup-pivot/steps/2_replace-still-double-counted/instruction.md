The L2 from the previous step still shows incorrect quantity — REPLACE orders are still double counted. At a price level the size shows twice expected, and the snapshot mismatch persists against the reference. You can see duplicate `order_id` lingering in the book after replay.

Fix the handling so that `REPLACE` (`R|seq|old_order_id|new_order_id|new_price|new_size`) with `old_order_id` and `new_order_id` removes the old exactly once and inserts the new exactly once at `new_price` with `new_size`, with no phantom left at the old price. The L2 quantities should match expected per level and there should be no duplicate `order_id` in the book. Do NOT yet handle `REPRICE` (`P|seq|order_id|new_price|new_size` same id) — that remains broken and will be fixed in the next step's pivot to in-place fencing.

Additionally, write a report to /app/2_replace-still-double-counted_report.json listing live orders with price, size, queue_position for verification.
