Production traces we just profiled show lookups dominate — 2M ExecutionReports, 10K cancel/replace chains. The sorted array linear scan for dedup plus the cumulative chain walk using CumQty (tag 14) is too slow, and we're getting stale values.

The exchange has announced CumQty is deprecated and now unreliable — venues send stale zeros for compatibility, only LastQty (tag 32) is guaranteed present on every Trade (ExecType=F, tag 150=F) in the new feed. Risk no longer wants flat net per symbol; they want gross exposure per symbol for limit checks.

Pivot `/app/reconcile.py` which you fixed earlier:

- Keep the CLI `python3 /app/reconcile.py <dropcopy> <output_json>` but change the output shape. It must now write `{"SYMBOL": {"buy": int, "sell": int, "gross": int, "net": int}}` where `buy` is total absolute buy quantity, `sell` total absolute sell quantity, `gross` = buy + sell, `net` = buy - sell, all ints, sorted keys. The old flat shape `{"SYMBOL": int}` must be removed — JSON values must be objects not ints.

- Stop reading CumQty entirely. Remove all parsing/use of tag 14 and any string `CumQty`. Quantity must come only from LastQty (tag 32). The tool must not contain `14` as a quantity source. This is the deprecation — keeping the fallback delta logic leaves stale counts.

- Use a hash map (Python dict) keyed by `(venue, exec_id)` where venue is tag 49 and exec_id tag 17 (fallback tag 34 MsgSeqNum) for PossDup dedup (tag 43=Y) instead of linear scan.

- It must still correctly dedup PossDup resends under the new feed.

In other words, drop the cumulative logic you added for carry/reset, switch index to hash, and drop net-only aggregation — produce buy/sell/gross/net and ensure no CumQty read remains.
Additionally, write a short JSON report of what you fixed to /app/3_pivot-to-gross-exposure-hash-index_audit.json.
