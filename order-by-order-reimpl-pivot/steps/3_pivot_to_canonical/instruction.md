New evidence from production: downstream aggregation double-counts because your snapshot includes size-0 retained entries, and the in-place re-key path from the previous steps causes lookup misses under load. Traces we just profiled show tail-enqueue is faster and canonical. The exchange confirmed the old dialect was a bug.

Pivot your implementation at `/app/build_book.py` to canonical book semantics:

- When an execution `E` drives displayed size to exactly 0, remove the order from its level immediately — do NOT retain `ref:0`. Snapshot must not contain any entry with `:0` size.
- On every Replace `U`, always remove the old entry and enqueue a fresh order `new_ref`/`price`/`size` at the tail of (side, new price) level, regardless of whether price changed or size increased/decreased — never keep queue position. The re-key in-place path must be removed.
- Snapshot still prints bids by price desc, asks by price asc, orders in queue order as `ref:size`, but now without any zero-size entries.

We will validate byte-exact against a new reference generator that implements this canonical behavior on held-out feeds whose refs, prices, sizes are disjoint from previous samples. Also assert old quirks are absent: your builder must not contain a code path that retains zero-size orders after `E`, and must not keep priority on `U`.

Keep the same CLI: feed path as first arg, snapshot to stdout. `/app/quirks_report.json` is no longer required but leaving it does not break grading; main check is stdout and absence of old logic.
Write report to /app/3_pivot_to_canonical_report.json.
