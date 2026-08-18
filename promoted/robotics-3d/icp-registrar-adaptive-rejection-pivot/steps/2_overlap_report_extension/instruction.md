Now we also need an overlap diagnostic alongside the pose.

For every successful registration, additionally write /app/overlap_report.json containing a single JSON object with exact keys source, target, final_n_corr, final_keep_pct, final_robust_cost, final_step_scale, overlap_score. source and target are basenames of the input files, the four final_* fields are the last-iteration values from your verbose trace (iter, n_corr, keep_pct, robust_cost, step_scale), and overlap_score is final_n_corr divided by min(len(source), len(target)). Keep the existing pose output behavior unchanged — this file is additive.

We will run your registrar on held-out pairs and check that /app/overlap_report.json exists with those exact keys and that its numeric fields match the actual verbose output for that run.
