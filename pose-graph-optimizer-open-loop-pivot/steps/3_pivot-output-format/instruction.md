The optimizer is now correct for batch evaluation, but the live SLAM pipeline that consumes it just profiled it: the sorted-by-id output with `theta` wrapped to `(-pi, pi]` causes discontinuities and extra sorts on every frame — lookups dominate and chaining odometry fails when angles jump from pi to -pi.

We need to pivot the output contract for this live use. Switch the trajectory file to follow the input pose graph's node file order (the order nodes appear in the input file, not sorted by id ascending) and emit continuous unwrapped `theta` without wrapping to `(-pi, pi]` — accumulate rotation so the trajectory is smooth for odometry chaining. Drop the sorting and wrapping work we added for batch eval; the output must NOT be sorted by id and must NOT have `theta` normalized to `(-pi, pi]`.

Keep the MLE correctness from before (same optimizer, same handling of loop direction and full covariance). The invocation stays `python3 /app/optimize.py <input> <output>` but output ordering and angle handling changes as above.

Also emit a small diagnostic report at `/app/loop_report.json` listing each loop closure edge that was direction-corrected. Each entry should have `edge_id` and `was_inverted` bool. This file is needed for the loop validation step downstream.

First node still remains the fixed datum anchor.
