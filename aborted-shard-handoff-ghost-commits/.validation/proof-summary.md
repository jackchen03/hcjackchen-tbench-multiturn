# Final Phase-2 proof binding

Bundle: `bundle-sha256-v1:b6f9c7aa7f6df8c94c4a34e6605c68645b2e424d9eab639404688b58b3d5f24d`

- Static: zero Critical/High findings with the archived handoff supplied through `TBENCH_AUTHORING_DIR`.
- Docker chain: `.validation/chain-20260903T194715Z.json`.
- Starter/Step-1 no-op: rejected, 4 executed, 0 skipped, 4 failed.
- Step-1 oracle: 4 executed, 0 skipped, 0 failed.
- Step-2 under-execution (the carried Step-1 implementation, representing the stale-control/source-only mutant family): rejected, 4 executed, 0 skipped, 1 failed.
- Step-2 oracle: 4 executed, 0 skipped, 0 failed.
- Boundary 1→2: `NOT_REQUIRED`; Step 1 permits compatible future capability.
- Valid-alternative control: the Step-2 recovery/certificate implementation is a materially extended compatible superset of the Step-1 record-oriented implementation and is replayed through the exact Step-1 grader by the chain boundary phase; it remains accepted. Behavioral tests impose no struct/helper/journal-encoding checks.
- Public/hidden separation: public trace uses generation 17 and payload `late`; graded scenarios use generations 29/33/47/52 and disjoint payloads and identities.
- Grader isolation: each candidate is compiled with `CGO_ENABLED=0`, copied into a fresh chroot containing only the binary and read-only trace, then executed as uid/gid 10002. Tests, expected assertions, and host paths are outside that root.
- Hygiene and working/projected fingerprint equality are rechecked after closure generation.
