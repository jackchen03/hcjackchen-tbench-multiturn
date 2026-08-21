# Step 1 — recover a binary PLY that looks valid but has wrong geometry

We have a binary PLY point cloud at `/app/data/scan_corrupted.ply` that is broken. Weirdly it looks completely fine: `plyfile` or `open3d` opens it without error, vertex count matches, `x`, `y` distribution looks plausible, `cat` shows a tidy header with `format binary_little_endian 1.0`, `element vertex`, `property float x`, `property float y`, `property float z`, `property uchar red`, `property uchar green`, `property uchar blue`, `element face`, `property list uchar int vertex_indices`. There is a loader at `/app/naive_load.py` that "successfully" reads it — try it.

But if you compare its xyz and faces to our ground-truth, they don't match at all — positions are scrambled, faces don't connect. It's not precision; the bytes on disk don't match the layout declared in the header, so standard loaders produce plausible-looking garbage. I've tried obvious one-place fixes and geometry stayed wrong — don't just stare at one field.

Write a script whose invocation is fixed as `python3 /app/recover.py <corrupted.ply> <out.ply>`: read the first arg (damaged file), write a clean cloud to the second arg path. Output must be standard `binary_little_endian 1.0` binary PLY, `element vertex` property order strictly `property float x`, `property float y`, `property float z`, `property uchar red`, `property uchar green`, `property uchar blue` (float32 xyz plus uchar rgb, so 15 bytes per vertex, no padding), `element face` as `property list uchar int vertex_indices`. Keep original model units — no scaling or translation — and keep vertex order and face order identical to the original.

More steps will follow; conserve your recovered files under `/app`.
