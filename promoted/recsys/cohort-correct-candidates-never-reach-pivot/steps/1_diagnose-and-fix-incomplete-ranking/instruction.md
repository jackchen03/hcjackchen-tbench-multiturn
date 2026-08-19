The online recommendations look slightly off.

A cohort of items we know users would really like keeps ranking near the bottom and almost never makes the final top list. Sampling shows most of these suppressed items come from the backfill retrieval path, while primary path items rank normally. Scores coming out of the ranker are all non-zero and look plausible in magnitude, so the pipeline does not crash and logs stay clean. Overall NDCG is only slightly down, easy to miss, but if you look specifically at backfill recall@10 the drop is huge — items that should be in the top 10 don't get in.

Retrieval is fine — the items are retrieved and enter ranking. The frozen linear ranker weights in `rec/rank.py` are correct and must not be edited. The bug is in what is fed into the ranker before scoring, in `rec/features.py`.

Fix the root cause so high true-affinity items from backfill return to where they belong, without breaking existing primary users.

After fixing, `python -m rec.run` must write per-user top results to `/app/output/recommendations.csv` with header `user_id,item_id,rank`, each user top 10 by score descending, rank 1..10 where 1 is highest.

There are more steps after this; keep resources.