Your trim fix helped — partial-overlap pairs now match. But we still see divergence when the clouds contain outlier points.

Probe the outlier case: /app/samples/outlier_0.src.ply → /app/samples/outlier_0.tgt.ply . On that pair your current /app/icp_reimpl.py converges to a different basin than /app/oracle (rotation >1e-4, translation >1e-4). The oracle's stderr log on this pair shows survivors that include large-residual correspondences — so something about its residual handling on the fringe is different from a simple rejection.

Extend /app/icp_reimpl.py to also match the oracle on outlier-contaminated pairs while preserving your previous partial-overlap fix. The same pose tolerance (1e-4 rad rotation, 1e-4 translation) and same CLI (`--source --target --out` row-major 4x4) still apply. Keep using /app/icp_reimpl.py as the entry point.

Don't repeat earlier context here — your previous fix remains in place.

