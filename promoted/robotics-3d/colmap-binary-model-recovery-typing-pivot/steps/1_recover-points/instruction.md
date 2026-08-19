The SfM point cloud recovered from our COLMAP-style binary model is almost entirely wrong.


For now, focus only on the 3D points. Write a recovery program. You can use `/app/sample_model/` together with `/app/sample_gt/points.npy` to locate the issue and verify your fix. Grading will use a different corrupted model with the same corruption pattern, so don't hardcode answers — reconstruct from the byte level.

Your program must be invoked as: `python3 /app/recover.py <corrupted_model_dir> <out_dir>` where `<corrupted_model_dir>` contains `cameras.bin`, `images.bin`, `points3D.bin` and `<out_dir>` is created if missing. In this step produce only:

- `<out_dir>/points.npy`: a numpy array, `dtype` `float64`, shape `(N, 3)`, each row is `x, y, z` in COLMAP world coordinates, original scale, no transform, all rows sorted by `point3D_id` ascending.

More steps will follow; conserve resources.