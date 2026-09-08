# Final Phase-2 proof binding

Bundle: `bundle-sha256-v1:419e1bc57d7cd71f064f916c5be7ca5c9f97461c7fcc2784be6d9d64a70c722c`

- Static: zero Critical/High findings with the archived handoff supplied through `TBENCH_AUTHORING_DIR`.
- Docker chain: `.validation/chain-20260903T194505Z.json`.
- Starter/Step-1 no-op: rejected, 4 executed, 0 skipped, 2 failed.
- Step-1 oracle: 4 executed, 0 skipped, 0 failed.
- Step-2 under-execution (the carried Step-1 implementation, representing the conservative keep-all/full-scan mutant family): rejected, 5 executed, 0 skipped, 4 failed.
- Step-2 oracle: 5 executed, 0 skipped, 0 failed.
- Boundary 1→2: `NOT_REQUIRED`; Step 1 permits compatible retirement capability.
- Valid-alternative control: the exact grader accepts materially different page histories and projection orders, and certificate validation is representation-neutral: any authoritative typed dependency path is accepted rather than an oracle-selected path. The Step-2 implementation is replayed through the exact Step-1 grader as a compatible superset.
- Public/hidden separation: public IDs and Rome/7 values are absent from the held-out page, projection, payload, snapshot, continuation, and graph cases.
- Grader isolation: the candidate Python runtime and current `/app/src` are copied into a fresh chroot; the process drops to uid/gid 10002 before execution. Tests, expected values, verifier state, and host paths are absent from that root.
- Hygiene and working/projected fingerprint equality are rechecked after closure generation.
