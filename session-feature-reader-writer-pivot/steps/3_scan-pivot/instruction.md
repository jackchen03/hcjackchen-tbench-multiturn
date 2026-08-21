The full decode-then-filter path we built for answering "which sessions contain item X" turned out to be too slow on production traces — profiling shows decoding every event's ts_delta and recency_bucket dominates and allocating dicts for all sessions blows memory for large shards.

Switch to a direct byte-scan for this query and drop the full-decode work we added for it. Add a new module at /app/session_scan.py exposing find_sessions_with_item(path, target_item_id) that returns a list of session_id ints sorted ascending, each being a session containing the target item at least once. It must parse the shard's raw bytes itself — read header magic, session count, per-session session_id, event count, anchor_item_id and item-id deltas — and skip the ts/recency payload bytes entirely to decide containment. The result must match what filtering fully decoded sessions would give, on held-out shards you have not seen.

Crucially, the scan hot path must not call or import decode_shard — the old approach of decoding everything then filtering must be removed from this query path. Leave /app/session_codec.py's public API from previous steps intact; just add the new scan module and keep heavy dict allocations out of the scan.

Title keywords session, feature, pivot must appear.
