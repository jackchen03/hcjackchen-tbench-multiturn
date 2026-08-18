Profiling your fixed implementation on dense scans from /app/samples_dense shows the bottleneck. On /app/samples_dense/dense_0.src.ply → /app/samples_dense/dense_0.tgt.ply the nearest-neighbor search dominates (>30s wall time). See /app/profile_trace/README.md for the trace and time budget — the deployment requires <5 seconds on this dense pair while preserving exact basin matching.

The oracle's brute-force exact nearest-neighbor search (deterministic tie-break by index) was never meant to scale. Switch the correspondence search in /app/icp_reimpl.py to a deterministic indexed structure that preserves the exact same pose outputs on all previous pair types. For example, using scipy.spatial.cKDTree with an explicit deterministic tie-break (if two points are equidistant within 1e-12, pick the smallest original index) achieves the same basin.

Importantly, this pivot away from brute-force restores coherence at scale: remove the nested double loops over all point pairs from /app/icp_reimpl.py. The graded solution must not contain brute-force O(N^2) distance loops and must finish the dense pair within the budget. Pose tolerance stays 1e-4 rad and 1e-4 translation on all clean, partial-overlap, outlier, and dense pairs.

Keep the CLI: --source --target --out as row-major 4x4.

