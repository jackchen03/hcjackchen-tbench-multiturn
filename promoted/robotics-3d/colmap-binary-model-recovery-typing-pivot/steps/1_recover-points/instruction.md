The SfM point cloud recovered from our COLMAP-style binary model is almost entirely wrong.

We export `cameras.bin`, `images.bin`, `points3D.bin` from an SfM pipeline. Each file is little-endian variable-length records. The "official" byte layout is documented in `/app/README.md` — `/app/naive_read.py` implements it faithfully. That reader parses the shipped sample model `/app/sample_model/` without any error, returns plausible counts and a reasonable bounding box, but when you compare its output to the reference truth for that same model in `/app/sample_gt/points.npy`, only the very first 3D point is correct and the rest are garbage. The files can be parsed, but the geometry is wrong. The underlying on-disk bytes do not match the documented layout.

For now, focus only on the 3D points. Write a recovery program. You can use `/app/sample_model/` together with `/app/sample_gt/points.npy` to locate the issue and verify your fix. Grading will use a different corrupted model with the same corruption pattern, so don't hardcode answers — reconstruct from the byte level.

Your program must be invoked as: `python3 /app/recover.py <corrupted_model_dir> <out_dir>` where `<corrupted_model_dir>` contains `cameras.bin`, `images.bin`, `points3D.bin` and `<out_dir>` is created if missing. In this step produce only:

- `<out_dir>/points.npy`: a numpy array, `dtype` `float64`, shape `(N, 3)`, each row is `x, y, z` in COLMAP world coordinates, original scale, no transform, all rows sorted by `point3D_id` ascending.

More steps will follow; conserve resources.
