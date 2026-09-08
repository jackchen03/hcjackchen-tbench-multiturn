# Cumulative Phase-2 finding inventory

| ID | Risk | Disposition | Evidence |
| --- | --- | --- | --- |
| F01 | Newest checksum-valid slot accepted despite unsealed/incoherent lineage | FIXED | C01 and Step-1 hidden cases |
| F02 | Stop-at-first-damage loses later acknowledged work | FIXED | C02 and post-pocket accepted transaction |
| F03 | Magic/header-CRC decoy accepted | FIXED | C02 and wrong-predecessor decoy |
| F04 | Transaction IDs alias across incarnations/lineages | FIXED | C04 and reused-ID cases |
| F05 | Partial or aborted controls applied | FIXED | C03/C05 and missing-ack/abort cases |
| F06 | Output/provenance coupled to public fixture | FIXED | C06/C14, twelve independent hidden cases |
| F07 | Physical rewrite invalidates source cursors | FIXED | C07 and source hash map |
| F08 | Step 2 silently recomputes a different decision ledger | FIXED | C08 and exact decision-byte check |
| F09 | Nearest-record/byte-delta cursor mapping breaks atomicity | FIXED | C09-C13 cursor-class probes |
| F10 | Hidden grader accepts missing, skipped, malformed, or crashed output | FIXED | canonical `test.sh`, strict subprocess and JSON assertions |
| F11 | Compatible Step-2 superset rejected at Step 1 | FALSE_POSITIVE | boundary is contract-justified NOT_REQUIRED |
| F12 | Phase-1 authoring artifacts leak into projected bundle | FIXED | author-only inputs moved to named external archive; final allowlist/projection check |
| F13 | Instruction immutability unproven | FIXED | pre-build baseline and final hash comparison |
