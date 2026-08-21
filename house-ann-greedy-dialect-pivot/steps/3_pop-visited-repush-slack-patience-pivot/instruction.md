# Pop-visited re-push and slack patience pivot

Your tie fix cleared most equidistant clusters, but remaining mismatches all share a pattern: they occur where a node is reachable via two paths before expansion, and a few threshold queries still differ by 1-2 members.

New evidence from profiling the failing witness queries:
- Legacy marks visited at POP time, not push time, and allows re-pushing the same slot even if that slot already sits in the frontier (frontier is NOT de-duplicated). Those stale re-push entries consume push_ctr values and shift the tie positions of every node pushed afterwards — the coupling is entirely through push_ctr.
- Stop condition is not "best frontier worse than worst result". Legacy stops when d_frontier > d_k * beta with beta=1.25, i.e. slack times beta, OR after P=3 consecutive expansions that did not improve d_k (patience). Whichever fires first. Let d_frontier be min distance among frontier entries whose node is unvisited, d_k be k-th smallest distance among popped-so-far (inf if <k popped), beta=1.25, P=3.

Your previous optimization that marks visited at push and de-duplicates frontier, and uses canonical best-candidate-worse-than-worst-result stop, is wrong and must be removed. Pivot to pop-visited re-push and slack patience stop.

Implement in /app/annsearch.py: seed frontier with entry_point and its first s=4 neighbors each with fresh push_ctr in stored order, heap keyed by (distance, push_ctr). Pop min, if slot already visited skip (stale re-push), else mark visited at POP, append to popped, and for each neighbor NOT yet visited push it with fresh push_ctr even if frontier already contains that neighbor — i.e. no frontier dedup, re-push allowed. Maintain since_improve and last_dk for patience. Stop when d_frontier > d_k * 1.25 or since_improve >=3. Final list = all popped sorted by (distance asc, push_ctr asc) of the entry that was actually popped, map slot to item_id, top-k.

Remove the old visited-at-push and canonical stop logic — final /app/annsearch.py must NOT contain a visited check at push time that prevents re-push, must NOT de-duplicate frontier, must contain re-push, beta=1.25, P=3, slack, patience, POP semantics. Keep load_graph and knn_search(graph, q, k) signature, keep /app/anngraph/ intact, and still importable.

This step is the pop-visited re-push slack patience pivot with beta=1.25, P=3, push_ctr, slack, patience, visited marked at POP, frontier NOT de-duplicated, re-push.
Additionally, write a short JSON report of what you fixed to /app/3_pop-visited-repush-slack-patience-pivot_metrics.json.
