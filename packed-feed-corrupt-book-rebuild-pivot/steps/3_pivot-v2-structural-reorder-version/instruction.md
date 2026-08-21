After fixing offsets and per-field byte order for the common message, the sample still shows a residual mismatch — a handful of AddOrder messages still enter the book at wrong price/size/symbol, and their later Cancel/Execute misfire, leaving a few levels off and VWAP diverged. The divergence is small on the sample but larger on other feeds that have more of this variant.

New evidence: every message starts with a 2-byte header already noted — `msg_type` then `version` (1 or 2). The current code ignores `version` and decodes every AddOrder as one layout (v1). Look at the byte dump for AddOrder with `version`=2 — its fields are structurally reordered, not just a constant change. The sample under `/app/sample/` exercises at least a handful of these v2 AddOrders across two or more symbols, so v2 is empirically discoverable from shipped material, but the oracle you have is aggregate (final book + VWAP per symbol) not per-message.

Pivot the implementation: AddOrder has two structurally different layouts gated on the `version` byte. One layout places `sym_len`+`symbol` before `price`/`size`, the other places `price`/`size` before `sym_len`+`symbol`. The fixed-width prefix through `side` is identical for both versions. You must branch on `version` and decode each variant with packed offsets and per-field endianness, preserving that `price` is big-endian and everything else little-endian, and ensuring `order_id` lookups for Cancel and Execute resolve.

Remove the old single-layout assumption and any single-format-string decode that uses one endianness for all fields. The final `/app/replay.py` must still satisfy `python3 /app/replay.py <feed_file> <output_json>` producing `{"bids": [[price, size], ...], "asks": [[price, size], ...], "vwap": int}` with integer ticks, bids descending, asks ascending, size>0 only, and exact VWAP floor, with no duplicate `order_id` phantom and no garbage lengths from misreading `price` bytes as `sym_len`.

Ensure Cancel (`X`) and Execute (`E`) with `exec_size` still work — Execute contributes `price*exec_size` to VWAP at the resting order's price looked up by `order_id`.
The output for this step must include price/size before sym_len.
This step must handle fixed-width prefix through side correctly.
Additionally, write a report to /app/3_pivot-v2-structural-reorder-version_report.json.
