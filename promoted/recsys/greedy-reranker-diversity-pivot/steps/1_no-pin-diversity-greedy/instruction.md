We're replacing the old re-ranking service with our own implementation. For the same request, the new implementation must produce exactly the same final ordering, position by position, otherwise we cannot safely roll it out.

In `/app/corpus/requests.jsonl` there is a batch of sampled requests from prod. Each line is a JSON object with `request_id`, `k` (number of positions to output), `candidates` (list of items each with `item_id`, `base_rel`, `category`, `segment`), `pins` (object where key is slot index as string and value is `item_id` to pin at that slot), and a `ranking` field which is the old service's final ordering — a list of `k` item_ids in position order — our ground truth.

For this first step, focus only on requests with no pinned slots. Those are the majority and they already show the core problem: my intuitive re-ranker matches on simple requests but once the same category repeats, the tail diverges even though the top high-score items agree. The greedy re-ranker diversity handling is the issue.

Write `/app/rerank.py` exporting `rerank(request)` where the request dict does NOT include the `ranking` field (same shape as above minus `ranking`). It must return a list of `k` ints (item_ids) in order. There is also a no-pin-only slice at `/app/corpus/no_pin_requests.jsonl` with the same schema for quick self-checking.

This step's hidden tests only use requests where `pins` is empty and will compare your output to the legacy `ranking` exactly. More steps follow; do not implement handling for `pins` yet — keep the file focused on the diversity greedy part. Keep resources.
