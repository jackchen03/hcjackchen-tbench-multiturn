Now that the incomplete ranking is fixed and backfill items show up, we still have low visibility into how specific cohorts are doing over time.

Add a metrics module that reports recall for the cohorts that were previously suppressed. It should compute per-cohort recall@10 and write it to `/app/output/cohort_metrics.json` with keys `backfill_recall_at_10` and `category_recall_at_10` plus `ndcg_at_10` as floats. Reuse the feature assembly you already fixed — don't re-implement ranking or re-pin the retrieval paths.

The metrics should be runnable via `python -m rec.metrics` after `python -m rec.run` has produced `/app/output/recommendations.csv`. When you run it on the visible sample users it should show backfill recall recovered but category-sensitive recall still low — that will motivate the next change.

Keep the existing top-10 output contract from step 1 intact.
