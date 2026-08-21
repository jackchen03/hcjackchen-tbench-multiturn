# Step 2 — add normals and a validity report

Your recovered mesh from step 1 is now at `/app/recovered.ply`. The downstream mesh checker needs per-vertex normals for shading and a small report to gate the next stage.

Compute per-vertex normals as area-weighted average of incident face normals, then write an enriched PLY at `/app/recovered_with_normals.ply`. Keep it `binary_little_endian 1.0`, keep the original vertex properties plus `nx`, `ny`, `nz` — final vertex order must be `property float x`, `property float y`, `property float z`, `property uchar red`, `property uchar green`, `property uchar blue`, `property float nx`, `property float ny`, `property float nz` (so 27 bytes per vertex, no padding), and keep `element face` as `property list uchar int vertex_indices` with same face order.

Also emit `/app/report.json` with at least `vertex_count`, `face_count`, `bbox_min` [x,y,z], `bbox_max` [x,y,z] — mins and maxs taken from the recovered xyz (model units, same as step 1).

Don't re-derive the raw scan layout; rely on what you already produced.

