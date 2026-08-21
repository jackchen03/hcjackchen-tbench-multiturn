# Pose graph files

Invoke `python3 /app/optimize.py <input pose graph file> <output trajectory file>`.

`NODE id x y theta` declares initial poses. `EDGE edge_id from_id to_id type dx dy dtheta c0 c1 c2 c3 c4 c5` declares ODOM or LOOP constraints and six packed covariance values. Batch output is `id x y theta`, sorted by id with theta normalized to `(-pi, pi]`; the first node in the file is fixed.
