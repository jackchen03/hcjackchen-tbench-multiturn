We run team-draft interleaving for A/B. Two rankers A and B each give an ordered item list. Per session we have a seed, k, and we build a slate of length k using a seeded coin per position to pick which ranker contributes its next unused item.

We have a problem: the on-disk log column `owner` desyncs, and replaying the documented protocol from the format note doesn't reproduce the real slate that was served on collision sessions. Samples in `/app/interleaving/samples/` give you `served_slate` (the true served item order that actually went to users) plus `seed`, `ranker_a`, `ranker_b`, `k`, `log`, `clicks`. The doc at `/app/interleaving/format_note.md` describes the canonical team-draft — that doc is incomplete.

Your job this step is to figure out the real interleaving rule by reconciling your replay against the sample `served_slate`. The mismatch only appears in sessions where a ranker's most-preferred item was already taken by the other ranker. Cat/less of the log looks fine — you need to probe the seeded stream.

Write `/app/replay.py`. When run as `python /app/replay.py` it must read `/app/interleaving/samples/*.jsonl` for self-check and `/app/interleaving/sessions.jsonl` (dev copy, same schema as samples but without served_slate) and write `/app/output/slate.jsonl`. Each line is JSON with `session_id` and `slate` array (the true served order, item_ids) in the same order as `sessions.jsonl`.

Do not trust the `owner` column — it's the broken logger output. Use `numpy.random.Generator(numpy.random.PCG64(seed))` with `rng.integers(0,2)`. Get the sample slates to match byte-for-byte before writing your output. Don't modify anything under `/app/interleaving/`.

Output contract hidden tests check: `slate.jsonl` has one entry per input session, matching true slate exactly. No credit or corrected log output is expected yet.
