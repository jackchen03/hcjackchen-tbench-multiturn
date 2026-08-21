Now that geometry is correct, downstream needs a quality gate that proves the fixes are actually present.

Keep your fixed pipeline from step 1 — same /app/sfm_reconstruct.py, same /app/tracks.py, same /app/triangulate.py, same --scene and --out flags, same .npz with key points N×3 float64 world coordinates and same datum/scale. Don't re-derive those.

Add that after each reconstruction, the pipeline also writes /app/recon_report.json with at least these integer fields:

- duplicate_image_track_count
- total_tracks
- points_count

duplicate_image_track_count must be 0 after the fix, and the JSON must be derived from the actual run (total_tracks and points_count matching the built tracks and exported points), not hard-coded. The report should be overwritten on each run.

The existing chamfer checks must still pass on held-out scenes.
