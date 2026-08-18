The JSON/npy dump you built was a stopgap for debugging. The production COLMAP pipeline doesn't consume `poses.json` or `points.npy` — it expects a standard COLMAP binary model that tools like `/app/naive_read.py` and COLMAP's own `read_write_model.py` can parse directly.

We've profiled the downstream workflow: the custom dump requires a bespoke loader that we don't want to maintain, and every team ends up reimplementing it. The repaired data should be re-serialized into the honest standard layout documented in `/app/README.md` (no off-by-one counts, no mis-typed fields) so that naive readers work.

Pivot the recovery: instead of dumping custom JSON/npy, directly produce a repaired binary model directory that is valid per the standard layout. The previous workaround files are no longer needed — remove that indirection.

Same entrypoint `python3 /app/recover.py <corrupted_model_dir> <out_dir>` now must produce in `<out_dir>`:

- `cameras.bin`, `images.bin`, `points3D.bin` all in standard COLMAP binary layout (little-endian, per `/app/README.md`), with true counts and true field widths, containing the recovered true poses and true points you previously dumped as JSON/npy. `cameras.bin` can be copied/transcoded from the input (it was never corrupted) but must be valid standard.

And must **not** produce `poses.json` or `points.npy` anymore — the absence of the old workaround will be checked. The repaired `images.bin` must use observation record `x f64, y f64, point3D_id i64` (24 bytes) with correct `num_points2D`, and `points3D.bin` must use correct `track_length`. A standard reader like `/app/naive_read.py` on `<out_dir>` should now return correct geometry.
