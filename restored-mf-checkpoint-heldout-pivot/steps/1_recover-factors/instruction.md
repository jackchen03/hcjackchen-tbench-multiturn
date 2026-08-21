The training team upgraded the parameter-server checkpoint writer. Since then the restored MF model we get from the live checkpoint scores held-out (user, item) pairs completely wrong. The model loads fine with no errors, but the dot-product scores don't match the offline baseline.

All files for this checkpoint live in /app/checkpoint/ — that includes model.blob, wal.idx, meta.json, and a FORMAT.md note. We tried to read the new checkpoint directly with the old serving loader at /app/serving/loader.py and the scores are still wrong — the storage layout it assumes is clearly not the current version.

I dropped a set of known-good sample scores in /app/sample_scores.csv, each row is user_id,item_id,expected_score where expected_score is the dot product of that user factor and that item factor. You can use it to check whether your restored factors are right, but note this file is only a subset — evaluation will use a disjoint set of held-out pairs (heldout) that you haven't seen.

Restore the factors and make the heldout scores match.

Restore the model correctly: rebuild the user factor matrix at /app/out/P.npy and item factor matrix at /app/out/Q.npy, both float32, row index equals logical id (row u of P is user u's factor, row i of Q is item i's factor), factor dimension comes from dim in meta.json. The evaluator will load those two matrices and dot held-out pairs against hidden truth — every pair must match within tolerance — so don't hardcode to the sample, truly restore every entity. There are more steps after this, so conserve resources.
