Compliance just finished an audit of the exchange's allocation fairness. The finding is in `/app/specs/allocation_v2.md`: the top-order priority carve-out that favored the first-in order at best price is being retired.

Starting now, the exchange dialect is pure pro-rata on original resting quantities with the iterative `MIN_FILL` re-pool retained, no carve-out. Remove the carve-out logic entirely — if you keep `ceil(Q/2)` or `min(top.qty, ceil(Q/2))` handling your fills will be wrong under the new spec and old allocation will not match.

The new remainder tie-break is `participant_id` then `order_id`, not `seq`.

Also downstream PnL reconciliation now requires a per-participant aggregation report. After fixing `/app/matcher.py` for allocation v2, write `/app/reports/pnl_impact.json` as a JSON list of objects with exact keys `event_id`, `participant_id`, `total_filled_qty`, where `total_filled_qty` is the sum of `filled_qty` for that participant's orders in that event.

This pivot completes the allocation dialect change — ensure the carve-out is absent and the report exists.
