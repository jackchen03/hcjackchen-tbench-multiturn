# Contract map

| Contract | Tests |
|---|---|
| S1 V3 success and V2 rejection | `test_v3_positive_v2_negative` |
| S1 flag/header/binary alignment | `test_all_build_layers_are_aligned` |
| S1 probe unchanged | `test_probe_integrity` |
| S2 effective limit covers 8192 and nobody owns/writes state | `test_effective_limit_and_state_access` |
| S2 soak, health, zero EMFILE | `test_soak_health_and_zero_emfile` |
| S2 bounded retry plus kill/restart | `test_kill_restart_and_bounded_policy` |
| S1 carry regression | `test_step1_regressions_remain_green` |

Behavioral checks accept make or direct-gcc builds and main-unit or drop-in configuration. The limit is a lower bound rather than an exclusive value.
