# Control results

Bundle fingerprint: `bundle-sha256-v1:25512efaf2354273c6dbbbc7dcc8f15e71251e2b49c77cda461ed2d7a285e5a8`

The exact shipped graders were run in Docker. The alternate report witness retained the semantic implementation but emitted an additional solver-chosen diagnostic object; all three graders accepted it: step counts `4/4`, `3/3`, and `3/3`, with zero skipped. Raw output is in `controls/aliquot-{1_reconstruct-custody,2_integrate-partial-reruns,3_compute-reagent-recall}-alt.log`.

Rejected plausible-wrong controls:

| Mutant | Result | Evidence |
| --- | --- | --- |
| barcode/latest display join starter | rejected, 3/4 failed | `chain-20260903T193952Z.log`, step-1 DO-NOTHING |
| quantity-only receipt matching | rejected, 3/4 failed | `controls/aliquot-mut-quantity.log` |
| latest-timestamp rerun winner | rejected, 2/3 failed | `controls/aliquot-mut-latest.log` |
| ancestor closure ignoring exact signed scope | rejected, 2/3 failed | `controls/aliquot-mut-scope.log` |
| broad current-result/plate-style recall | rejected, 1/3 failed | `controls/aliquot-mut-plate.log` |
| pooled cross-specimen available volume | rejected, 1/3 failed | `controls/aliquot-mut-pool.log` |

Public and hidden cases are disjoint in IDs, barcode values, quantities, topology, signing keys, rerun records, lots, and assay minima. Hidden expectations are constructed from their latent case definitions before candidate execution. Candidate subprocesses run as uid/gid 65534 with no-new-privileges, a scrubbed environment, read-only case files, and a private writable output directory; `/tests` is mode 0700 before candidate execution.
