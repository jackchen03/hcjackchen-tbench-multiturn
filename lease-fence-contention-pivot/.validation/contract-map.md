# Contract map

| Contract | Graded evidence |
|---|---|
| S1 durable 8-byte BE fence and exact grants | `test_durable_exact_grants_and_reopen`, `test_threaded_grants_are_gap_free` |
| S1 token/HWM gate and exact JSON shape | `test_fencing_hwm_and_exact_log_shape` |
| S1 no premature Step-2 artifacts | `test_step2_artifacts_not_premature` |
| S2 >=16 durable stripes | `test_sixteen_independent_durable_stripes` |
| S2 independent progress | `test_stripes_do_not_share_a_global_lock` |
| S2 signed carried-log retirement | `test_signed_retirement_binds_carried_log` |
| S1 regression under S2 | `test_global_step1_contract_still_works` |

Truth is derived from test-selected operations, not candidate output. Alternate JSON whitespace, lock implementation, and stripe internals are accepted. A 32-stripe implementation is valid. Phase 2 corrects the handoff's inventory-only omission of the signed solver-authored artifact.
