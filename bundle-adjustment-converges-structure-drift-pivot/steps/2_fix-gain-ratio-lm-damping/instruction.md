Consistent weighting fixed the search direction, but the iteration trace still shows early exit.

After your fix, on /app/sample_problem.npz the solver reports converged quickly with mean reprojection low, yet on held-out rigs with wide sigma range (0.1–5 px) the reduced chi-square stays elevated and median point error vs GT stays above tolerance. Look at the per-iteration log: rho (gain ratio) stays tiny, lambda (damping) inflates fast, step norm collapses within a few iterations and the loop declares converged far from the true minimum.

The loop measures actual reduction as weighted cost drop C(x)-C(x+dx), but predicted reduction is computed by a separate helper linear_predicted_reduction_raw that reuses raw pixel errors via reproj_error_px and the unwhitened Jacobian — so pred is unweighted while actual is weighted. Fix B: make predicted reduction use the same weighted linearization that solved the step (weighted g and H) via linear_predicted_reduction_weighted, so rho = actual / pred_weighted is meaningful and lambda adapts correctly.

Write a short JSON /workdir/lm_gain_fix.json with before/after rho and lambda trace to show the fix — this file will be checked.

Rely on carried context — same /app/ba_refine.py, same --input/--output, same points/poses keys, same datum fixing first camera — don't re-derive those. Focus on gain ratio, damping, step norm, and predicted vs actual reduction mismatch.
