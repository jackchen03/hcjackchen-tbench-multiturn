# Phase-2 contract map

Bundle fingerprint is filled by final evidence generation.

| ID | Step | Contract / hidden dimension | Solver-visible authority | Evidence |
| --- | --- | --- | --- | --- |
| C1 | 1 | Variable-width operands at one-, two-, and three-byte boundaries | Step 1: compact variable-width packing and final emitted program | `test_local_expansions_preserve_handlers_roots_markers_and_back_edge` |
| C2 | 1 | Forward/backward branch targets | Step 1: preserve branch destinations | first two Step 1 tests |
| C3 | 1 | Nested handler ownership after local expansion | Step 1: preserve selected exception handlers | first two Step 1 tests |
| C4 | 1 | Live-root sets at safepoints | Step 1: preserve live roots at every GC safepoint | first two Step 1 tests |
| C5 | 1 | Adjacent/terminal zero-width markers and prefixed operations | Step 1 explicit marker/prefix clauses | all Step 1 tests |
| C6 | 2 | Three-to-five fused phases and A-B-A duplicate origins | Step 2: preserve every ordered occurrence | `test_fusion_preserves_duplicate_order_and_phase_local_state` |
| C7 | 2 | Phase-specific throws and roots | Step 2 explicit handler/safepoint clauses | same test |
| C8 | 2 | Complete inclusive encoded size and manifest budget | Step 2 first paragraph | `test_complete_encoded_size_is_inclusive_and_within_manifest` |
| C9 | 2 | Prior result, marker, handler, roots, and debug behavior | Step 2: all earlier behavior remains correct | `test_regression_preserves_width_markers_roots_and_handlers` |
| C10 | 2 | Multiple independent fusion groups retain order | Step 2 exact ordered phase sequence | `test_distinct_fusion_groups_remain_separate_but_ordered` |

Non-unique surfaces: final semantic-owner organization and fused ledger organization. The grader
uses public CLI behavior and stable public artifact accounting only; it does not inspect helper
names, source shape, opcode numbers, or a preferred internal data structure.

Transition 1 -> 2 is additive. Compiler/runtime source and semantic ownership are carried and
mutated. Public examples and interface documentation are read-only. No artifact is retired. Future
Step-2 fixtures are absent from the initial image. Early compatible fusion is permitted, so the
boundary is `NOT_REQUIRED`; Step 2 reasserts representative Step-1 behavior exactly.
