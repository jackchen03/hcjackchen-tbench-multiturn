# Contract and transition map

Fingerprint is recorded by the final proof artifacts.

| ID | Requirement | Visible authority | Graded evidence |
| --- | --- | --- | --- |
| A-S1-1 | late admitted effects apply once in order | Step 1 paragraphs 1-2; public contract | `test_late_admission_and_noncommutative_order` |
| A-S1-2 | full incarnation/sequence identity and original reply | Step 1 paragraphs 1-2 | `test_full_identity_and_original_reply_frontiers` |
| A-S1-3 | unrelated shard remains writable | Step 1 paragraph 1 | `test_unrelated_shard_keeps_progressing` |
| A-S2-1 | stale generations cannot change generation 42 | Step 2 paragraphs 1-2 | `test_stale_controls_cannot_steal_generation_42` |
| A-S2-2 | preserve full identity/frontiers through abort | Step 2 paragraphs 1-2 and inherited Step 1 | `test_regression_preserves_full_identity_and_frontiers` |
| A-S2-3 | C-only certificate and covered trimming | Step 2 paragraph 2 | `test_only_final_destination_can_issue_covered_gc` |

Transition 1→2 carries the modified source, ticket records, and split frontiers. Generation-41 ownership is retired after abort; generation-40/41 control authority is retired once generation 42 begins. Step-2 fixture/truth files remain verifier-only. The transition is additive, so compatible future capability is accepted and over-execution is `NOT_REQUIRED`; Step 2 reasserts the prior exact effect, reply, identity, and progress behavior.

Hidden values use generations 29, 33, 47, and 52 plus payloads absent from the public trace. The public-path-hardcoding mutant, scalar sequence-key mutant, old-generation fence mutant, source-only reconciliation mutant, stale-control mutant, premature-GC mutant, and starter/no-op are the named negative families. Record-oriented and event-fold implementations, and separate versus embedded certificate representations, are non-unique surfaces accepted by behavioral grading.
