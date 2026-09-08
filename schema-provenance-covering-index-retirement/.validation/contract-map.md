# Contract and transition map

Fingerprint is recorded by the final proof artifacts.

| ID | Requirement | Visible authority | Graded evidence |
| --- | --- | --- | --- |
| S-S1-1 | covering projections equal heap values across alias changes | Step 1 paragraph 1; contract §§1-2 | projection-context and cycle tests |
| S-S1-2 | compact witnesses and deterministic projection bounds | Step 1 paragraph 2; contract §3 | witness/counter test |
| S-S1-3 | no heap fallback or reindex | Step 1 paragraph 2 | witness/counter and regression tests |
| S-S2-1 | exact least closure with post-migration roots | Step 2 paragraph 1; contract §§4-6 | exact-closure test |
| S-S2-2 | valid certificate root authorities and typed paths | Step 2 paragraph 1 | certificate test |
| S-S2-3 | preserve carried covering reads | Step 2 paragraph 2 and inherited Step 1 | regression test |
| S-S2-4 | delta-bounded, idempotent maintenance | Step 2 paragraph 2; contract §6 | cold-scale and no-change tests |

Transition 1→2 carries page witnesses, typed metadata edges, open snapshot roots, continuation roots, and counters. Unreachable nodes and stale pre-migration roots are retired; verifier-only graph mutations and expected closure are future artifacts. Step-2 regression executes the carried covering read after retirement. Step 1 permits a compatible retirement superset, so runner boundary over-execution is `NOT_REQUIRED`; Step 2 itself behaviorally rejects conservative retention.

Certificate paths are solver-chosen. The grader validates root authority and each path edge, and accepts any valid path rather than matching the oracle witness. Hidden IDs, values, projection orders, graph shapes, and cold components are disjoint from the public example. Named negative families are global-alias canonicalization, current-only repair, shallow witnesses, direct-root GC, keep-all GC, full rescans, public-ID hardcoding, and starter/no-op. Eager and lazy witness strategies plus SCC and per-root-contribution retirement are non-unique valid surfaces.
