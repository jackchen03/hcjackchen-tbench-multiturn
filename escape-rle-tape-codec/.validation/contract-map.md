# Contract map

- S1 instruction lines 1-4 -> exact TABLE/RUN/TRAILER/SIZE blocks for all three public tapes; tests derive bytes from the operated reference outputs.
- S2 lines 1-3 -> exactly four named rules and four SEED evidence lines; tests independently parse public fixtures and reference outputs.
- S3 lines 1-3 -> `/app/encoder.py IN OUT`, byte equality on disjoint hidden inputs, and reference-delegation isolation.
- Fixture dimensions: split cap, FE literal handling, checksum reset/coverage, held-out mixed runs. Positive controls and alternatives use the same assertions as the oracle.
- `difficultyProof=pending_phase2`; local correctness is not trajectory evidence.
