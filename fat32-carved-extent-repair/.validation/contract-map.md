# Phase-2 contract map

Bundle fingerprint: `bundle-sha256-v1:cf8cc00ca1864ebccfb89785f318c5fc89fb37ce426d3d9fb24ade1fa6beeb92`

| Step | Contract | Authority | Shipped evidence |
| --- | --- | --- | --- |
| 1 | `fat_decision.txt` is exactly one `HEALTHY=FAT1|FAT2` line | `steps/1_triage/instruction.md:3` | `test_public_decision_and_repaired_image` |
| 1 | repaired image preserves the intact FAT and makes both FATs identical | `steps/1_triage/instruction.md:3` | public byte comparison plus flipped-table hidden replay |
| 1 | `repair.sh <src> <dst>` derives either healthy table and shifted damage range | `steps/1_triage/instruction.md:3-5` | `test_repair_cli_derives_flipped_healthy_table` |
| 1 | source image is not repaired in place | `steps/1_triage/instruction.md:3` | read-only source plus unchanged/different-image hash assertion |
| 2 | manifest is name-sorted JSON with the exact four-key schema | `steps/2_carve/instruction.md:3` | `test_public_manifest_matches_independent_chain_truth` |
| 2 | start, size, name, and hash come from the FAT1 chain and SQLite `filemeta` | `steps/2_carve/instruction.md:3` | independent raw FAT walker and SQLite validation |
| 2 | deleted entries and clobbered high word are restored in the image | `steps/2_carve/instruction.md:3` | active-dirent/raw-byte verification and clean fsck |
| 2 | `carve.sh` generalizes across different heads, names, hashes, and row totals | `steps/2_carve/instruction.md:3-5` | `test_carve_cli_accepts_disjoint_names_hashes_and_heads` |
| 2 | Step-1 FAT equality and artifacts remain intact | inherited Step 1 | `test_restored_image_contains_exact_manifest_bytes_and_preserves_step1` |
| 2 | an early valid Step-3 file is a compatible superset, not prohibited | Phase-1 `overExecMap[2]=NOT_REQUIRED` | `test_compatible_early_outcome_artifact_is_not_forbidden` |
| 3 | image passes `fsck.vfat -n` clean | `steps/3_verify/instruction.md:3` | `test_public_outcome_recomputes_rows_hashes_and_cleanliness` |
| 3 | every extracted file hash equals its manifest hash | `steps/3_verify/instruction.md:3` | independent raw-chain hashing plus `verify.sh` |
| 3 | row count is the sum of `SELECT COUNT(*) FROM records` | `steps/3_verify/instruction.md:3` | independent SQLite count and changed-row hidden fixture |
| 3 | outcome is exact and newline-terminated | `steps/3_verify/instruction.md:3` | exact byte assertions |
| 3 | `verify.sh` generalizes to a different manifest and row total | `steps/3_verify/instruction.md:3-5` | `test_verify_cli_recomputes_disjoint_row_total` |
| 3 | Step-2 manifest/image and scripts remain valid | inherited Steps 1-2 | `test_prior_manifest_and_carve_artifacts_remain_valid` |

Non-unique surfaces are covered by `alt_dd_cmp`, `alt_chain_copy`, and `alt_raw_read`. Public and hidden controls differ in FAT selection/range, recovered heads/names/hashes, and verification row totals.
