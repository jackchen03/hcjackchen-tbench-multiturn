We profiled the fixed pipeline on larger scenes with heavy match transitivity. Trace shows track building dominates runtime — the current merge checks only endpoint collision via _endpoints_collide and then linearly scans image lists, so scenes with long chains pay O(N^2). And downstream mesh pipeline now expects PLY, not NPZ — parsing .npz is slowing it.

Switch the reconstruction export to binary PLY. When invoked with --scene and --out, it should now write a PLY file at the --out path (e.g. /tmp/out.ply) containing vertices as xyz float64-equivalent world coordinates in the same datum/scale as before (camera 0 identity, baseline pinned). The old NPZ export path that writes key points must be removed — we assert it no longer creates a valid NPZ with points key.

Also optimize the track builder to O(1) image presence via hash map — implement _components_share_image that checks full-component image overlap via dict/set lookup, and remove the old helper _endpoints_collide entirely. No linear scan fallback.

Write marker /workdir/ply_export_proof.json after successful PLY export with fields {"ply_written": true, "optimized_merge": true}.

Chamfer checks on the PLY vertices must still pass (mean and tail), and quality report /app/recon_report.json must still be written with duplicate_image_track_count == 0, now derived from the optimized structure.
