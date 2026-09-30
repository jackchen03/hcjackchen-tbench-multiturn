# Transition evidence

Bundle fingerprint: `bundle-sha256-v1:35b8eb86a7efec7902cf03ef4c6270f067f01bfaac7dd25142f4ad3a41063e3a`

## 1 -> 2

- Type: compatible additive context-following.
- Carried state: /app/topk.py exact_topk behavior.
- New artifact: /app/diagnosis.json.
- Regression: exact pair values and tie ordering are rerun on disjoint streams.
- Under-execution: a tie-flipped carried exact implementation fails while a valid diagnosis is present.
- Future isolation: diagnosis is absent initially.
- Over-execution: NOT_REQUIRED; the current Step-1 contract does not prohibit diagnosis.

## 2 -> 3

- Type: motivated production-path override while retaining callable exact behavior.
- Carried state: /app/topk.py and /app/diagnosis.json.
- New artifacts: approx_topk and /app/RETIREMENT.signed.
- Regression: exact_topk remains callable and exact; retirement cites the carried diagnosis hotspot.
- Under-execution: wrong carried hotspot with ground-truth citation fails the own-file comparison.
- Future isolation: approximation and retirement are absent initially.
- Over-execution: NOT_REQUIRED; affirmative preservation in Step 2 accepts the complete Step-3 superset.
