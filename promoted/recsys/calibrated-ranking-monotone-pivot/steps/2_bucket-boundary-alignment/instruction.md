Your previous loader fix improves agreement on the sample, but on a larger held-out set that is heavy on feature values landing exactly on bin edges, rankings are still permuted in the middle.

The offline training path buckets with `np.digitize` using its default boundary semantics (value equal to an edge goes to the right bucket). Serving must match offline bucketing exactly for calibrated ranking to be consistent. Check the serving bucketization helper — the current boundary check handles edge equality differently.

Fix the serving bucketization to match offline semantics. After this fix, running `python -m rec.serve` must still write `/app/output/rankings.csv` with header `user_id,item_id,rank`, 10 per user ranked by final calibrated score descending, tie by `item_id` asc, and now it must exactly match the offline reference on both the sample and an edge-heavy held-out set that you haven't seen.

Keep the same constraints: don't edit base ranker weights, training data, edges file, or artifacts. Conserve the calibration loader fix you made.

Note: this follow-up relies on the calibration loader you fixed earlier — don't re-explain or re-pin that path, just add the missing boundary alignment.
