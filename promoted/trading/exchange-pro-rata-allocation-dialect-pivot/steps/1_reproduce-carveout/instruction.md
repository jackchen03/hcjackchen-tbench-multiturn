We recently swapped in a new matching module at the exchange. On regression checks we noticed a weird symptom: for every matching event the total filled quantity your module computes matches the reference blotter exactly, but the per-order filled quantities for each resting order are wrong in many books, which breaks downstream position and PnL reconciliation.

The container has the buggy module at `/app/matcher.py` and a reference blotter sample at `/app/blotter/sample_blotter.json`. Each entry in the blotter gives the book at the best price — a list of resting orders with `order_id`, `participant_id`, `price`, `seq`, `qty` — plus the incoming aggressor quantity `incoming_qty`, and the old engine's per-order fills `filled_qty` including zeros. The old engine source is gone; you only have its inputs and outputs.

Figure out the exchange's real pro-rata allocation dialect from that sample and fix the matcher so it reproduces the reference per-order fills exactly for every event in the sample.

Keep the existing CLI `python /app/matcher.py <book.json> <out.json>` — it must read a book JSON (list of events with `incoming_qty` and `resting_orders`) and write a fills JSON list of objects with exact keys `event_id`, `order_id`, `filled_qty` for every resting order in every event, including zero fills. For example an output file may be written to `/tmp/out.json` or `/app/fills.json` depending on what the harness passes — respect the output path argument.

This is the exchange's pro-rata allocation dialect task; there are more steps after this, so conserve resources and keep the fix minimal.
