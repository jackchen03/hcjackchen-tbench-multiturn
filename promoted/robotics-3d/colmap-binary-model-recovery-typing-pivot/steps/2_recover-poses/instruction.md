Fixing the points fixed the point cloud, but the camera poses are still all wrong except the first image.

The naive standard reader in `/app/naive_read.py` still returns plausible image counts but garbage poses for `image_id >= 1`. We have ground truth for the sample at `/app/sample_gt/poses.json` showing the magnitude of the error.

Extend your recovery to also recover true camera poses. Keep the points recovery you already have working.

Now `<out_dir>` must contain both:

- `points.npy` as before (`float64`, `(N, 3)`, sorted by `point3D_id`)
- `poses.json`: a JSON object where keys are `image_id` as **string**, values are objects with fields `"qvec": [qw, qx, qy, qz]`, `"tvec": [tx, ty, tz]`, `"camera_id": <int>`, `"name": <str>`. Quaternion uses COLMAP convention: Hamilton, order strictly `qw, qx, qy, qz`, world-to-camera rotation `X_cam = R(qvec) · X_world + tvec`. Keep original values, coordinate system, units — no transform, no normalization, no scale. Include all registered images.

Same invocation: `python3 /app/recover.py <corrupted_model_dir> <out_dir>`. More steps will follow.
