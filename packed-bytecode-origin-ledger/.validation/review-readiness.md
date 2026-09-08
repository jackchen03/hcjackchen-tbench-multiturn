# Review-readiness audit

- Final static gate: no findings.
- Carried Docker chain: Step 1 starter rejected (3/3 failed), oracle accepted (3/3); Step 2 under-execution rejected (1/4 failed), oracle accepted (4/4). No tests skipped.
- Boundary 1→2: `NOT_REQUIRED`; Step 1 does not forbid compatible early fusion.
- Reference lifecycle: no solver-visible reference or expected-output artifact exists in the image.
- Exact truth: verifier-owned interpreter logic only; no goldens in the runtime image.
- Public/hidden split: byte- and semantic-family-disjoint; public-path hardcoding mutant rejected.
- Valid alternatives: stable-ID side table and iterative out-of-line phase ledger accepted by the shipped graders.
- Mutants: provisional-coordinate map, deduplicated origins, disabled fusion, and public hardcoding rejected.
- 4D: compiler/runtime state is mutated and Step 2 reasserts Step-1 width, marker, root, handler, result, and debug behavior; examples/docs are read-only.
- Grader isolation: candidate runs only through `/app/bin/policyvm`; verifier never imports candidate modules and deletes each source input before running the self-contained artifact.
- Dependencies: all fetched packages are exact-pinned and installed from bundled wheels.
- Calibration: Oracle/model completion remains `unmeasured` in README; local Oracle-x3 is reference stability evidence only.
- Instruction hashes match the pre-build baseline.
