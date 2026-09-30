# Gzip reproducibility to content-addressed layer

Step 1 repairs `/app/pack.sh` so equivalent trees produce identical gzip archives and a strict manifest. Step 2 carries that exact manifest and packer forward, then pivots the artifact of record to an uncompressed layer ordered by content hash.

The transition is non-decorative: the second oracle consumes the manifest produced by the first step, while its verifier rechecks the carried packer and manifest behavior. The earlier gzip may coexist because Step 1 does not forbid compatible future functionality; the 1→2 over-execution boundary is therefore contract-justified `NOT_REQUIRED`.

## Completion measurements

| Runner | Step 1 | Step 2 | Whole task |
|---|---:|---:|---:|
| Oracle | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured |
