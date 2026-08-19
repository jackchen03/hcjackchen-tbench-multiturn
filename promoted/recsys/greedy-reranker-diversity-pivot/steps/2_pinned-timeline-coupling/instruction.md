Your no-pin diversity greedy re-ranker now passes on non-pinned traffic, but pinned requests are still broken — diverging from the third position onward when `pins` are present.

Add support for `pins` in the same `/app/rerank.py` `rerank(request)` you already built. The contract stays the same: input is a dict with `request_id`, `k`, `candidates` (each with `item_id`, `base_rel`, `category`, `segment`), and `pins` mapping string slot index to `item_id`. Output is a length-`k` list of `item_id`s.

When you diff the legacy `ranking` against a post-hoc approach that diversifies first then forces pinned items into slots, you will see the divergence is not random — the pinned item changes who wins the slots after it. Use the full corpus at `/app/corpus/requests.jsonl` (about 40% have 1-2 pins) which includes ground-truth `ranking` for self-checking, plus the dedicated pinned slice at `/app/corpus/pinned_requests.jsonl`.

Reuse the diversity logic and conventions you discovered — do not re-pin or re-explain them. This step's hidden tests include both no-pin and pinned requests and require exact match to legacy `ranking`, plus that pinned item_ids appear at their reserved slots.

There is one more step after this that will change the pin handling requirement, so conserve the current behavior cleanly. For this step, pins MUST contribute to diversity — their categories must be counted in the evolving prefix when computing the penalty for later slots (legacy behavior). The opposite (pin-free) will be the next step's pivot.