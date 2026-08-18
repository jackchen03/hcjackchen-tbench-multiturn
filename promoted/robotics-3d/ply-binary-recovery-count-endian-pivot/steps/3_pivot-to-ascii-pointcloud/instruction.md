# Step 3 — pivot to ASCII point cloud, drop colors and faces

We profiled the perception pipeline on traces from the scanner. It never uses `red`/`green`/`blue` or `face` — it discards them immediately, and the binary `list uchar int vertex_indices` parser dominates load time. The team also wants PLY dumps to be diffable in PRs, which binary isn't.

The previous assumption that we need a full binary mesh with colors and faces is now wrong for the end artifact. Switch the final deliverable to a lightweight oriented point cloud.

Read `/app/recovered_with_normals.ply` from last step, write `/app/final.ply` as `format ascii 1.0` with only `element vertex` and 6 properties `property float x`, `property float y`, `property float z`, `property float nx`, `property float ny`, `property float nz` — one ASCII line per vertex in that order, same order as your enriched file. Do not include any `element face`, and ensure there is no `red`, `green`, `blue` property left — our downstream service rejects files still carrying those. This is a deliberate pivot away from the binary mesh we shipped before; absence of the old face list and color columns will be checked.

