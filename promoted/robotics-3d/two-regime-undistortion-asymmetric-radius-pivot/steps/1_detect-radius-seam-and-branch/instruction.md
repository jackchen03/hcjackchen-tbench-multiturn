We have a wide-angle camera undistortion system that must run in production. The production reference is an opaque binary at /opt/ref/undistort_ref. We keep a Python reimplementation at /app/undistort.py exposing undistort_points(points, coeffs) where points is a list of [x, y] distorted normalized points and coeffs is [k1, k2, k3, p1, p2], returning a same-length list of undistorted points in input order.

Currently /app/undistort.py matches the reference perfectly in the central disk — near the image center you see almost zero error — but if you plot error versus radius you see a sharp seam at a fixed distorted radius. Past that ring, our output diverges from the reference, and toward the image corners the error grows to several pixels. The source looks textbook-correct and passes central checks, so the bug is invisible to code review alone.

You can probe /opt/ref/undistort_ref freely. It is called as `/opt/ref/undistort_ref <camera.txt> <points_in.txt> <points_out.txt>` with lines "x y". Sample camera is at /app/sample_camera.txt, and some sample points are at /app/samples/inner.txt. Compare your current /app/undistort.py against the reference across radius, and also reproject reference outputs through the forward distortion model to see if they are a true mathematical inverse.

This is a two-regime undistortion problem: the reference behaves differently inside vs outside a fixed radius branch. Your first job is to detect the seam location and implement the branching so that the outer regime is deliberately non-converged (single step, not iterated to convergence). For this step, fix /app/undistort.py so that:

- It has a radius branch keyed on distorted radius rd = hypot(x_d, y_d) against a fixed threshold you must recover by radial scan.
- Inner (rd < threshold) remains a converged fixed-point true inverse.
- Outer (rd >= threshold) is a truncated single fixed-point step (not converged). You may start outer from identity init u0 = x_d for now.

Keep the file at /app/undistort.py and keep undistort_points(points, coeffs) signature unchanged. After this step, the inner disk must match the reference within 1e-6 per component, and outer points must show non-zero reprojection residual when pushed through forward distortion (proving non-converged), unlike the current fully-converged baseline.

More steps will follow; conserve your fix and the probing method for later extensions.