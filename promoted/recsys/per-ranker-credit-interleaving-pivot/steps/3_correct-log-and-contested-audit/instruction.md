That credit fix works for eval, but downstream still consumes the broken `owner` log, and we just found sessions where the contested-top condition triggers more than once in the same session — a one-time extra-draw patch still leaves the tail shifted by 2-3 coins.

So pivot: we need a full corrected owner log and an audit of where the logger diverged. The simple credit-only output isn't enough for the pipeline fix.

Extend what you built to also emit the corrected log. Write `/app/correct_log.py` (you can have it call into your existing `credit.py` logic or merge into one file, as long as both entrypoints work). When run as `python /app/correct_log.py` it must read `/app/interleaving/sessions.jsonl` and write:

- `/app/output/corrected_log.jsonl` — one JSON per session in input order, fields: `session_id`, `corrected_owners` (array length k of "A"/"B" = true owner per position), `contested_positions` (sorted array of position indices where the extra-draw condition fired), `owner_mismatch_count` (int: how many positions where `log` owner != true owner)
- Keep `/app/output/credit.csv` correct as before (regression). Running `python /app/credit.py` should still produce the right credit, and `correct_log.py` should produce both files.

Your detection of contested positions must fire every time the picked team's global top (`ranker_a[0]` or `ranker_b[0]`) was already in slate owned by the other team — not just the first time. That repeated trigger is what fixes the multi-collision sessions.

No sample file contains `corrected_owners` at grading time, so you must forward-replay from seed with the full rule — don't brute-force per-session coins to fit a slate.

Remove any reliance on sample `served_slate` during grading run. Grading uses held-out seeds and item ranges disjoint from samples.

