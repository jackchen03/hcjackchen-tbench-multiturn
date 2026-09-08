# Runtime and isolation audit

Bundle fingerprint: `bundle-sha256-v1:911bc6221b8904c4bb078fe5f334186fb33d2eaf39ffec8a4dc7e8d2d32f8df6`.

- Initial-image inspection found exactly the candidate binary/source, public
  fixture, module file, and `FORMAT.md` under `/app`.
- `/solution`, `/tests`, hidden stores, expected outputs, decision ledgers, and
  future recovery views were absent from the initial image.
- No opaque reference is advertised or shipped, so executable-magic and
  anti-delegation checks are not applicable.
- Hidden stores are created under `/tmp/codimango` during verification. The
  candidate runs as uid/gid 1001 and receives only a current store path and a
  candidate-owned empty output directory. Expected semantic objects remain in
  the root verifier process and are compared after candidate exit.
- Public and hidden stores are bytewise and semantically disjoint. The public
  lineage is `blue`; hidden Step-1 lineages are `hidden-700..711` and
  `hidden-757`; hidden Step-2 lineages are `cursor-911`, `cursor-919`, and
  `cursor-927`.
- Exact expected state, decision, provenance, source-hash, and replay values are
  generated in the mounted verifier and are not copied into the image.
