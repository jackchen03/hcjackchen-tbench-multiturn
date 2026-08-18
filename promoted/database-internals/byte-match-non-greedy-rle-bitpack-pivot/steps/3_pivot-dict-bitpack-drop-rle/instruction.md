# Pivot dict bitpack drop rle

Your byte-identical hybrid encoder from last step works on old workloads, but new production traces under /app/production_traces/*.json show its RUN path has <1% hit rate on high-cardinality columns and the reader's new policy rejects pages containing RUNs on these workloads. Profiling indicates dictionary encoding compresses better.

Switch your encoder at /app/encoder to match /verifier/dict_encoder instead. It reads the same stdin JSON {"values":[...]} and writes raw page bytes stdout with same header C0 plus u16 n, but uses dictionary plus bit-pack only — no RUN segments at all. Dictionary order is first-appearance. Width selection still uses even-rounding, tail padding still uses last real index, same MSB-first grouping you learned before.

Probe /verifier/dict_encoder on the production traces and other inputs to learn its dictionary segment layout. Update /app/encoder in place to produce output byte-identical to /verifier/dict_encoder for every input.

You must remove the RUN encoding path entirely — final /app/encoder must never emit a segment where control varint C has LSB 1, and must not contain code that emits RUN. Tests will assert absence of RUN segments by parsing pages and static scan for RUN emission. If you need a helper manifest, write it at /app/dict_manifest.json and implement helper build_dictionary.

The title keywords pivot dict bitpack drop rle must appear. The RUN path poor hit rate on high-cardinality columns motivated the change. Preserve header convention and even-width handling from previous steps as regression.
