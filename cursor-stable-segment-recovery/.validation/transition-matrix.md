# Transition 1 → 2

- Prior authority: all acknowledged-only recovery, canonical decision,
  provenance, CLI, and determinism behavior remains authoritative.
- Delta/override: physical rewriting becomes invalid; immutable source hashes
  and a recovery view replace any rewritten store as cursor authority.
- Mutated/replaced: candidate cursor/view implementation. Evidence is Step-2
  view and resolver behavior.
- Read-only: exact DECISIONS bytes and PROVENANCE. Step-2 tests and oracle hash
  and reuse them without modification.
- Retired: in-place repair authority and byte-delta cursor translation.
- Future isolation: hidden Step-2 stores, cursor probes, and truth exist only in
  the mounted Step-2 verifier.
- Regression: Step-2 verifier reruns and exactly compares Step-1 state,
  decisions, provenance, and deterministic bytes on its independent store.
- Under-execution: Step-1 code has no build-view/resolve behavior and fails.
- Over-execution: `NOT_REQUIRED`; Step 1 permits compatible supersets and has no
  solver-visible prohibition against cursor support.
- S1/S2/S3: yes/yes/yes—Step-2 oracle requires Step-1 artifacts, its prompt
  omits recovery rules, and its tests bind to those exact carried decisions.
