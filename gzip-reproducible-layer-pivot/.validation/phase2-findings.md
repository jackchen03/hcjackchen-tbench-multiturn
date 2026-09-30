# Phase-2 finding and contract inventory

Bundle: `gzip-reproducible-layer-pivot`

## Contract map

| ID | Step | Solver-visible authority | Shipped assertion |
|---|---|---|---|
| GZ-S1-CLI | 1 | instruction lines 8-10 | invoke `/app/pack.sh <srcdir> <out.tgz>` on multiple hidden families |
| GZ-S1-REPRO | 1 | lines 1-7, 11-12 | double-build and equivalent-tree archive bytes are identical |
| GZ-S1-CONTENT | 1 | lines 11-18 | archive has a one-to-one, duplicate-free member inventory with exact kinds and payload hashes |
| GZ-S1-MANIFEST | 1 | lines 12-20 | strict JSONL keys, base64 paths, hashes, complete coverage, ASCII path_b64 order, exact newline framing |
| GZ-S1-VARIATION | 1 | lines 3-8 | hidden pairs vary names, sizes, timestamps, owners, traversal order, Unicode/newline names, symlink, empty directory |
| GZ-S2-CLI | 2 | instruction lines 1-4 | invoke `/app/make_layer.sh <srcdir> <manifest> <out.tar>` |
| GZ-S2-FORMAT | 2 | `/app/LAYER_SPEC.md` named by instruction | uncompressed USTAR with uid/gid/mtime zero, empty uname/gname, no pax headers |
| GZ-S2-ORDER | 2 | instruction line 2 plus `LAYER_SPEC.md` | exact `(sha256, path_b64)` order |
| GZ-S2-COVERAGE | 2 | lines 3-5 plus `LAYER_SPEC.md` | exact manifest coverage; missing/mismatched entries fail and source extras are excluded |
| GZ-S2-CARRY | 2 | "your manifest" and coexistence sentence | consume the carried manifest, preserve its bytes, retain functional `pack.sh` and `release.tgz` |

Mapped rows: 10/10. Non-unique surfaces: S1 pack implementation and S2 layer implementation. The shipped verifier includes materially different Python/GNU-compatible control paths; final external alternative evidence is recorded separately.

## Transition 1 -> 2

- Carried read-only: `/app/pack.sh`, `/app/manifest.jsonl`, `/app/release.tgz`, `/app/src/`.
- Added: `/app/LAYER_SPEC.md`, `/app/make_layer.sh`, `/app/layer.tar`.
- Override: `release.tgz` ceases to be the artifact of record but remains allowed and behaviorally valid.
- Under-execution: Step 2 fails before `make_layer.sh` and `layer.tar` exist.
- Over-execution: `NOT_REQUIRED`; Step 1 contains no explicit prohibition on compatible layer support.
- Regression: Step 2 re-executes the carried packer on an equivalent metadata/order pair, checks identical bytes and unchanged carried manifest, then audits the final layer against the carried manifest.

## Findings

- `P2-GZ-001` — temporary verifier output directories inherited umask 022, preventing the demoted candidate from writing. `FIXED`: explicitly chmod task-owned output directories 0777; source and truth remain root-owned read-only.
- `P2-GZ-002` — an initial positive-control assertion assumed compressed output exceeded 1024 bytes. `FIXED`: removed the unjustified size threshold; semantic archive and manifest audits remain authoritative.
- `P2-GZ-003` — Step-1 successor boundary. `NOT_APPLICABLE`: Phase 1 explicitly classifies compatible supersets as allowed, so the chain records `OVER-EXEC NOT_REQUIRED`.
