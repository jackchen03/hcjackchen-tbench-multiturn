# Recover integer distance and ordered output

We are migrating online recall from an old closed-source ANN engine to our own Python implementation. The graph and vectors are the same, under /app/anngraph/ (our own disk format, not any open source lib) with spec in /app/anngraph/FORMAT.md. Retrieval code is in /app/annsearch.py with a working load_graph(path) and a textbook beam search knn_search(graph, q, k) that returns wrong ordered neighbors for many queries.

The base knn_search uses float L2 or wrong tie handling. The old engine computes distance as integer squared-L2 over int8 vectors in Python int / int64 with NO dequant, NO float. That matters because small integers mean exact ties are frequent. Also the final list should be ALL popped nodes sorted by distance, not a bounded result heap, and you must return a Python list of int item ids length k in order.

Fix /app/annsearch.py so that load_graph and knn_search(graph, q, k) keep the same signature, and knn_search returns an ordered list of k ints. You can self-check against the sample witness under /app/witness/queries.npy and /app/witness/neighbors.jsonl — those are legacy ordered top-10 lists for seeded int8 queries. At this stage aim to make far / unique-distance queries match exactly; near-equidistant clusters may still drift.

This step is about integer distance and ordered output. Keep the file path /app/annsearch.py, function load_graph, knn_search(graph, q, k), and graph dir /app/anngraph/. Don't implement per-push counter tie logic or pop-visited re-push or slack/beta stop yet — just get integer distance and all-popped sorted deterministic ordering working.

Title keywords recover, integer, distance, ordered, output must appear but fix is just integer distance and ordered output.
