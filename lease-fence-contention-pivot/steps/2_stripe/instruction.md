The hardened lease is correct but serialized: `python3 /app/profile_contention.py --workers 32 --ops 2000` shows all commits funneling through one global path.

Shard the step-1 lease into at least 16 stripes exposing acquire_stripe and commit_striped so stripes proceed in parallel, with each stripe keeping the step-1 durable contract for its own fence, mark, and log. Write /app/ORDERING_DROPPED.signed whose first line is GLOBAL_ORDERING=DROPPED and whose second line is the sha256 of the step-1 log.jsonl; cross-stripe commit order is retired and never checked.
