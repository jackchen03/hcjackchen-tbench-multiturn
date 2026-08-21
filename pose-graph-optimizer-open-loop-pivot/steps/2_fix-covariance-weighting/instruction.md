The shear is gone and the trajectory looks close, but on graphs with anisotropic loop covariances it still misses the reference by a few hundredths in RMS, so the hidden tests that check against the true weighted least-squares MLE still fail.

Your optimizer is still using a diagonal approximation of the information. Fix the remaining weighting so it builds the full symmetric 3x3 covariance from the six packed values per edge and uses its full inverse for optimization, reaching the correct MLE on all graphs including anisotropic loop constraints.

Keep the same invocation `python3 /app/optimize.py <input> <output>` and same output format as before (`id x y theta`, sorted by id, `theta` in `(-pi, pi]`). The first node stays fixed.
