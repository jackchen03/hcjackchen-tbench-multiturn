We have an in-house marching cubes extractor at /app/mymc.py that extracts a triangle mesh from a 3D scalar volume (.npy float array). Its CLI is `python3 /app/mymc.py <volume.npy> <isovalue> <out.obj>` and it writes Wavefront OBJ. On the same machine there is a reference extractor `refmc` on PATH with the same CLI `refmc <volume.npy> <isovalue> <out.obj>` but no source. This is the marching cubes extractor ambiguity case — the first step will probe before the later pivot to a full fix.

On smooth blob volumes both produce identical meshes. On volumes with thin necks, two lobes close to touching, or pinched tori, they disagree: often the vertex count matches but triangle connectivity differs, sometimes even the genus (number of handles/tunnels) differs. About 15%% of a larger test set hits this. Looking at a single mesh file does not reveal the bug; you need to compare the two sides.

Your task for this step is to build a reproducible probing harness that isolates the ambiguity decision. Create at least 2 custom synthetic volumes as .npy files under /app/probe_volumes/ and a JSON report at /app/probe_report.json.

The report must contain evidence for:
- that the per-face ambiguous decision in refmc depends on off-face corner values (not just the 4 corners of the shared face)
- that for two adjacent cells sharing an ambiguous face, refmc's choice tracks the lower-raster-index cell (x fastest, then y, then z) — the first cell to touch the face in raster order owns the decision
- that the decision is not a single global scalar offset

Do NOT modify /app/mymc.py yet — leave it as is for now. Only probing and reporting this step.

The report file /app/probe_volumes/ volumes and /app/probe_report.json must exist. Keep literal paths verbatim: /app/probe_volumes/ and /app/probe_report.json.
