Got the true slate replay working. Now using the true interleaving you recovered, fix the per-ranker click credit.

Each session has `clicks` — array of 0-based position indices that were clicked. The log's `owner` column still lies on collision tails, so you can't use it for credit. True credit is number of clicked positions whose true owner (from your forward replay with the extra-draw branch) is A vs B.

Extend your code to write `/app/credit.py`. Running `python /app/credit.py` must read `/app/interleaving/sessions.jsonl` and write `/app/output/credit.csv` with header `session_id,ranker_a_clicks,ranker_b_clicks`, one row per session in input order, integer counts.

You can reuse the replay logic you built in the previous step. Don't re-read the doc — assume the RNG and contested handling you already discovered. Self-check against `/app/interleaving/samples/` where each sample now also gives `credit` to verify.

Keep `/app/output/slate.jsonl` working — we still need it — but the graded file this step is `credit.csv`.

Don't emit corrected log files yet; that comes next. Do NOT emit `/app/output/corrected_log.jsonl` or any audit file in this step; the audit/corrected log is step 3 only.