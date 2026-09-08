# Control results

Bundle fingerprint: `bundle-sha256-v1:b7decd2fc8beaf4259f12bfa986eb0c01e9a11898bb9d315e23150d11dd83b57`

The exact shipped graders were rerun in Docker after the MetaCode instruction transaction. The alternate report witness retained the semantic implementation but emitted an additional solver-chosen diagnostic object; all three graders accepted it: step counts `4/4`, `3/3`, and `3/3`, with zero skipped. Raw output is in `controls-current/{1_reconstruct-custody,2_integrate-partial-reruns,3_compute-reagent-recall}-alternate.log`.

Rejected plausible-wrong controls:

| Mutant | Result | Evidence |
| --- | --- | --- |
| barcode/latest display join starter | rejected, 3/4 failed | `chain-20260903T193952Z.log`, step-1 DO-NOTHING |
| quantity-only receipt matching | rejected | `controls-current/mutant-quantity.log` |
| latest-timestamp rerun winner | rejected | `controls-current/mutant-latest.log` |
| ancestor closure ignoring exact signed scope | rejected | `controls-current/mutant-scope.log` |
| broad current-result/plate-style recall | rejected | `controls-current/mutant-plate.log` |
| pooled cross-specimen available volume | rejected | `controls-current/mutant-pool.log` |

Public and hidden cases are disjoint in IDs, barcode values, quantities, topology, signing keys, rerun records, lots, and assay minima. Hidden expectations are constructed from their latent case definitions before candidate execution. Candidate subprocesses run as uid/gid 65534 with no-new-privileges, a scrubbed environment, read-only case files, and a private writable output directory; `/tests` is mode 0700 before candidate execution.
