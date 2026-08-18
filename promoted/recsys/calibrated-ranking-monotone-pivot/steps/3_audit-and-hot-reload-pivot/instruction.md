The ranking correctness is now fixed, but we profiled serving on a 10k-item trace and the binary `calibration.bin` parsing path dominates latency — `struct` unpacking of the `CALB` magic and positional reads prevents live updates. Calibration will now be updated daily without restart, and SRE requires observability.

Pivot the serving implementation:

- Switch the calibration source from `/app/artifacts/calibration.bin` to `/app/artifacts/calibration.json` (same `(bucket_id, weight)` mapping you already recovered, but JSON with fields `bucket_id` and `weight`). The JSON file is already produced by training and present on disk; your serving code must read it.
- Implement hot-reload: on each invocation of `python -m rec.serve`, check the JSON file's mtime and reload if changed — don't cache a stale mapping.
- Write an additional audit artifact `/app/output/calibration_audit.json` containing per-bucket item counts and average final calibrated score for the last run: a JSON dict keyed by bucket id (as string) with `{"count": int, "avg_final_score": float}`.
- Remove the old binary parsing code path that handles `CALB` magic and `struct` unpacking — the grader will assert that binary parsing logic is absent.
- Keep `/app/output/rankings.csv` contract exactly: header `user_id,item_id,rank`, 10 rows per user, rank 1..10 descending final score, tie `item_id` asc, and correctness must still hold on edge-heavy held-out.

This is an overriding change: old approach (binary struct loop and positional list indexing) must be gone, new approach (JSON + mtime check + audit output) must be present. Motivation is latency and live calibration updates without restart.

After fix, `python -m rec.serve` must write both `rankings.csv` and `calibration_audit.json` under `/app/output/`.
