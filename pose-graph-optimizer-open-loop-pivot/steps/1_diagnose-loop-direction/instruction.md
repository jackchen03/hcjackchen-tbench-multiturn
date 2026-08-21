We have a 2D SE(2) pose graph optimizer at `/app/optimize.py`. It reads a pose graph file that contains initial node poses, a chain of odometry edges, and loop closure edges, each edge carrying a relative pose measurement and its covariance packed as six numbers.

If you integrate only the odometry edges in order (open-loop dead reckoning), the trajectory matches the true trajectory closely. But once loop closure edges are added and you run full batch optimization, the pose graph optimizer produces a trajectory that shears and twists at loop closures, visibly drifting from truth. Adding more loop edges makes the distortion worse, not better.

Fix the optimizer so that adding loop closures improves the trajectory instead of degrading it, and the shear at loop closures disappears on the sample graph. Keep the invocation as `python3 /app/optimize.py <input pose graph file> <output trajectory file>` and keep the output format: each line `id x y theta` separated by single spaces, sorted by node id ascending, `theta` in radians normalized to `(-pi, pi]`. The first node is a fixed datum and must stay at its initial pose from the input file.

Under `/app` there is a sample pose graph and its correct trajectory for self-check. Focus on making the open-loop odometry chain and loop constraints consistent in direction so the pose graph no longer shears.
