# Phase-1 contradictions

Phase 2 stopped before bundle implementation because the Step-2-to-Step-3 carried state and the future-artifact guards are internally inconsistent.

## Step 2 removes the condition that Step 3 requires

Step 2 explicitly requires HEARTBEAT and END-OF-SESSION packets to be skipped entirely: do not read payload and **do not register their SequenceNumber as received**. A correct Step-2 implementation therefore cannot leave a heartbeat sequence in packet-start dedup state.

Step 3's entire motivating failure says the current dedup has already marked the heartbeat's SequenceNumber as seen, so a later retransmit with the same start sequence is skipped wholesale. That state can exist only if Step 2 violated its mandatory rule. With the required Step-2 behavior, the heartbeat/retransmit start-sequence collision does not trigger the claimed bug; the retransmit's start sequence was never registered.

Per-message dedup may still be a desirable final design for overlapping data packets, but the stated cross-step symptom cannot be produced by the correct prior artifact. Phase 1 needs a different Step-3 fixture (for example two overlapping non-sentinel data packets with the same start) or must weaken Step 2, which would change its contract.

## Future sample paths are pre-staged

The handoff uses `/app/samples/with_heartbeat.mold` and `/app/samples/collision.mold` as over-execution artifacts for Steps 1 and 2. The shared environment specification, however, plants the step-specific debug captures under `/app/samples/` for agent use and says one shared environment covers all three steps. The step instructions themselves tell the agent to validate those fixed paths.

Consequently a do-nothing initial container can already contain the paths that predecessor tests are supposed to forbid. Keeping them makes existence-based guards fail before any solver work; hiding/staging them contradicts the declared planted state unless a verifier lifecycle is explicitly defined.

Phase 1 must repair the semantic transition and replace pre-staged input-path guards with solver-created future artifacts or a precise verifier-staging lifecycle.
