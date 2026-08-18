Your radius branch fix helped — the seam is now at the right place and the outer regime is non-converged as the reference is. But probing near the image mid-field still shows bias.

Probe the isolated radial case to fix the asymmetric radius initialization:

- Use /app/samples/near_outer.txt (points with 0.35 <= rd < 0.5) and /app/samples/radial_only_camera.txt (a camera where p1=p2=0) against /opt/ref/undistort_ref.
- You will see that with p1=p2=0 the reference outer step is not from identity init u0 = x_d, but from a radial-only warm start: u0 = x_d / radial(rd^2), where radial(rd2) = 1 + k1*rd2 + k2*rd2^2 + k3*rd2^3 and rd2 = x_d*x_d + y_d*y_d (distorted radius squared). Then exactly one fixed-point step: u1 = (x_d - tang) / radial(|u0|^2). This warm start matters — identity init gives ~3.8e-2 error in outer, while radial warm start drops near-outer error dramatically.

This is the asymmetric radius part of the two-regime undistortion: the outer regime evaluates radial at the distorted radius rd2 for the warm start, not at the current iterate.

Extend /app/undistort.py (keep it at same path) to implement this radial-only warm start for outer points, preserving your previous threshold and inner converged logic from step 1. Keep undistort_points(points, coeffs) signature unchanged and keep tangential term in the current-iterate domain for now (still using |u0|^2 for its r^2 slots).

After this step, your implementation should match the reference within 1e-6 on inner points and within 1e-3 on near-outer points from /app/samples/near_outer.txt when tested with /app/sample_camera.txt and /app/samples/radial_only_camera.txt. Far-corner points like /app/samples/far_corner.txt will still diverge when tangential coefficients are large — that's expected for the next step.

Do not restate earlier context; your previous fix stays in place.
