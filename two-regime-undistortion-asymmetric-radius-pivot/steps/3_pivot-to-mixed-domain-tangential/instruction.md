Your outer radial warm start fixed near-outer, but far corners with strong tangential distortion still fail.

Probe the far field with tangential stress:

- Compare reference vs your current code on /app/samples/far_corner.txt (0.5 <= rd <= 0.72) using /app/samples/tangential_stress_camera.txt which has large p1,p2, and also /app/sample_camera.txt.
- With p1=p2=0 you already match, but with non-zero tangential you see up to ~6e-4 normalized error that grows toward corners. This is the final quirk of the two-regime undistortion.

The reference's outer regime uses mixed-domain tangential evaluation — a pivot from the textbook undistorted-domain convention:

In outer (rd >= threshold), the tangential term tang uses distorted radius rd2 = x_d*x_d + y_d*y_d for its r^2 slots, while using u0 components for ux,uy factors:
  tang_x = 2*p1*u0x*u0y + p2*(rd2 + 2*u0x^2)
  tang_y = p1*(rd2 + 2*u0y^2) + 2*p2*u0x*u0y
Correct/uniform would use |u0|^2, but reference deliberately uses rd2 here. This asymmetric radius handling only matters inside the truncated outer single step, which is why fixing branch alone stayed red.

This pivot to mixed-domain restores coherence at scale: switch your outer tangential computation in /app/undistort.py to use rd2 (distorted radius squared) as above, and remove the old undistorted-domain tangential path for outer points. Importantly, inner regime must stay converged with tangential in undistorted domain (current-iterate), and outer must stay as radial warm start single step — only the tangential domain changes.

Keep file at /app/undistort.py and signature undistort_points(points, coeffs). After this final pivot, your code must reproduce /opt/ref/undistort_ref across full field of view — inner, near-outer, and far-corner — within 1e-6 per component for any camera, including held-out cameras never seen during probing. The reference can be called as `/opt/ref/undistort_ref <camera.txt> <points_in.txt> <points_out.txt>` but will be hidden at grade time, so your solution must not shell out to it.

Also verify absence of old approach: outer tangential must not use |u0|^2 for its r^2 slots anymore.
