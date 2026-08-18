# Fix tie order to per-push counter

Your previous fix made far queries match, but every near-equidistant cluster still mis-orders. The witness shows divergence concentrates on queries where top candidates have identical integer distances.

The legacy orders ties by a per-push counter push_ctr assigned when an entry enters the frontier, not by slot id or heap arbitrary order. Adjacency in /app/anngraph/ is stored sorted by slot id as a decoy — don't use that for tie-breaking. Track a monotonic push_ctr that increments on every push event and use (distance, push_ctr) as the heap key, and final ordering as (distance asc, push_ctr asc) of the popped entry.

Keep the same file /app/annsearch.py and same signature knn_search(graph, q, k). You still have load_graph and the graph under /app/anngraph/. At this point fix only the tie ordering to per-push counter push_ctr and ensure final list is all popped nodes sorted by that counter. Don't yet change visited marking to POP time or allow re-pushing same node, and don't yet implement slack/beta/patience stop — those belong to next step. You already have integer distance and ordered output from last step; carry those conventions forward.

This step talks about tie order per-push counter push_ctr, all-popped sorted, /app/annsearch.py, knn_search, load_graph.
