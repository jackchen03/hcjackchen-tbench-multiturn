# PolicyVM starter

`/app/bin/policyvm compile PROGRAM.json ARTIFACT.pvm` compiles a JSON policy.
`/app/bin/policyvm run ARTIFACT.pvm` prints one deterministic JSON result.

A program contains an ordered `ops` array. Operations have a unique `id`, an
`origin`, and one of `set`, `add`, `mul`, `branch_if_lt`, `marker`,
`safepoint`, `throw`, or `halt`. Arithmetic operations use `arg`; branches use
`arg` and a `target` label. An operation may carry a `label`, `prefix: true`,
`handler`, `roots`, and a fusion-group string in `fuse`. Markers are semantic
events that occupy zero opcode bytes. `step_events` and `sample_events` contain
the origin of every executed semantic phase in order, including markers.

The artifact is self-contained JSON. Its public `instructions`, `semantics`,
and `encoded_size` fields are stable. `encoded_size` counts each instruction's
declared opcode bytes plus every origin, handler, and root byte in the load-time
semantic table. A policy can include `max_encoded_bytes`; compile still emits
an artifact when that limit is exceeded so diagnostics can inspect it.
