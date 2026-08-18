We finished reproducing the legacy greedy re-ranker diversity pivot, but product audit says the legacy behavior we just cloned was actually a bug: pinned items should NOT mutate the diversity state of later slots. In prod it caused diversity collapse when a pin shared a category with organic candidates.

Pivot the implementation in `/app/rerank.py`. The new fixed spec is:

- Pinned items are still placed at their reserved absolute slots first.
- Then slots are filled in increasing index order using the same greedy scoring you already recovered (base_rel * SEGBOOST[segment] * penalty). However, `pin-free diversity` is now required — the category counts used for the penalty must be computed only from organic items that were selected by the greedy loop, ignoring any pinned items even if they sit in earlier slots. A pin at slot 2 must NOT change who wins slot 3+, diversity-wise.
- The final output still length `k`, item_ids in order, pins at reserved slots.

This invalidates the coupling you added in the previous step. The old code that counted pinned categories in the evolving prefix for diversity penalty must be removed — test will assert absence of counting pinned items for diversity.

Use `/app/corpus/fixed_spec_requests.jsonl` for self-checking — it ships `ranking` under the new fixed_spec semantics (pins present but ignored for diversity), and `/app/corpus/requests.jsonl` legacy corpus can still be inspected for contrast but is no longer the target.

After the pivot, `rerank(request)` must match the fixed_spec ranking exactly on held-out requests that include pins, while still matching legacy behavior on no-pin requests (since ignoring pins does nothing when pins empty). Ensure the old pin-affects-diversity logic is gone.
