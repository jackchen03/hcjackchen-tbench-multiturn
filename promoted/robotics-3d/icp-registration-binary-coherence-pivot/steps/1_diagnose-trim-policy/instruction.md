We have a point cloud registration tool that aligns a source cloud to a target cloud and outputs a 4x4 SE(3) transform. The production version is long gone — only an opaque reference binary remains at /app/oracle. We maintain a Python reimplementation at /app/icp_reimpl.py that is supposed to be a drop-in replacement and must match the reference pose: rotation error within 1e-4 rad and translation error within 1e-4.

Right now /app/icp_reimpl.py matches /app/oracle on clean, almost fully overlapping pairs like /app/samples/clean_0.src.ply → clean_0.tgt.ply, but diverges to a different basin on partial-overlap pairs like /app/samples/partial_0.src.ply. The wrong alignment can look plausible, but the pose is macroscopically different. We tried flipping the error metric and tuning overlap ratio — clean still passes, partial still diverges.

You can probe /app/oracle freely. It prints per-iteration diagnostics to stderr like `iter k rms=.. inliers=.. survivors=..` . Samples to use: /app/samples/clean_*.src.ply / .tgt.ply and /app/samples/partial_0.src.ply/.tgt.ply.

Fix /app/icp_reimpl.py so it converges to the same basin as /app/oracle on clean and partial-overlap pairs with compatible normals, restoring registration coherence — the same SE(3) basin, not just plausible alignment. Keep the CLI unchanged: `python /app/icp_reimpl.py --source <src.ply> --target <tgt.ply> --out <out.txt>` where out.txt is 4 lines of 4 space-separated numbers row-major. Entry file remains /app/icp_reimpl.py.

More steps will follow; conserve the oracle behavior and your fix for later extensions.

