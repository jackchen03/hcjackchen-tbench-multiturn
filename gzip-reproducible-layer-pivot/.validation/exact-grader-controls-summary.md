# Exact-grader controls

- Included bundle fingerprint: `bundle-sha256-v1:2aa10d734985b7e3bd8c9540e0525c4188d60923d5e98e2b4d7eefa0c0471e67`
- Runtime: `tbench-mt-gzip-reproducible-layer-pivot:validate`, `--network none`, one fresh container per case, tests delivered by writable private `docker cp`
- Result: 22/22 expected outcomes; 4 accepted controls, 18 rejected mutants, 0 mismatches, 0 skips
- Isolation: writable copied tests become directory mode 0700 and source mode 0600 before candidate invocation; a read-only test mount fails closed during collection before candidate execution.
- Machine-readable manifest: `.validation/exact-grader-controls-v1.json`
- Per-case stdout/stderr: `.validation/control-logs/*.log`
- Preserved earlier two-mutant evidence: `.validation/control-matrix.log` and `.validation/run-mutant-controls.sh`

Accepted controls:

- Step 1: `gnu_tar_clamp_chain`, `python_tarfile_impl`.
- Step 2: `gnu_tar_explicit_order_layer`, `python_tarfile_hash_order_layer`.
- The archived Step-1 samples used an obsolete empty-string directory digest. Their excluded control copies retain the named mechanisms but use `sha256(empty)`, as required by the final manifest contract; the manifest records this adaptation and the executed script hashes.

Rejected Phase-1 `failureAttribution` inventory:

- Step 1 (12): `plain_targz`, `gzip_n_only`, `clamp_no_manifest`, `legacy_space_manifest`, `wrong_file_payload`, `wrong_member_kind`, `wrong_symlink_target`, `source_mutation_matching_archive`, `uncompressed_tar_named_tgz`, `starter_noop`, `duplicate_member_exact_spelling`, `duplicate_member_dot_slash_alias`.
- Step 2 (6): `name_sorted_layer`, `gzipped_layer`, `src_recomputed_layer`, `manifest_mutation_matching_layer`, `nonnumeric_owner_metadata`, `targz_unchanged`.
- Impossible/non-applicable mutant IDs: none.
- Applicable over-execution boundaries: none (`overExecMap` is empty for both steps).
