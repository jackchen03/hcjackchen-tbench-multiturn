# Exact-grader controls

- Completed: `2026-09-30T17:48:55Z`
- Included bundle fingerprint: `bundle-sha256-v1:06fb263d455d1f5b3a94e495e982db33d0c9c7df993539e638d8cc891671250f`
- Runtime: `tbench-mt-ffmpeg-downmix-loudnorm-pivot:validate`, `--network none`, one fresh container per case, tests delivered by writable private `docker cp`
- Result: 17/17 expected outcomes; 6 accepted controls, 11 rejected controls, 0 mismatches
- Isolation: writable copied tests become directory mode 0700 and source mode 0600 before candidate invocation; a read-only test mount fails closed during collection before candidate execution.
- Machine-readable manifest: `.validation/exact-grader-controls-v1.json`
- Per-case stdout/stderr: `.validation/control-logs/*.log`

Accepted controls:

- Step 1: volume/highpass/pan, staging-corner variant, independent awk-DSP, and compatible early loudness processing.
- Step 2: single-pass and dual-pass loudnorm. The dual-pass witness uses ordinary `/tmp` for its transient first-pass log so it remains valid under uid demotion.

Rejected controls:

- Step 1: naive one-liner, starter/no-op, clip-first, no DC blocker, limiter-only, and public-path hardcoding.
- Step 2: peak-only, tag-only, unchanged Step-1 output, omitted 48 kHz resampling, and public-path hardcoding.

Boundary result:

- Phase-1 `overExecMap` is empty. A compatible early-loudness Step-1 superset passed, confirming that no unsupported Step-1 over-execution rejection was introduced. Step-2 unchanged output was rejected as under-execution.

Postchecks on the same included bytes:

- Handoff-aware static validation: PASS, 0 critical/high/medium/warn.
- Diff hygiene: PASS.
- Working/projected fingerprint equality: PASS.
- Instruction hashes unchanged: Step 1 `f5fcdb9c443484ea6358de3061b0a6e8f5923139c81f6dd16ef287289311e8b3`; Step 2 `023426e78545b30d251cb56541a51f019fd3576007b67349be23d5310bcbf471`.
- Residual `ffctrl-*` containers: none.
