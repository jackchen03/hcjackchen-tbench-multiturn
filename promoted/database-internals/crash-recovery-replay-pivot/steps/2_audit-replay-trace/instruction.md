# Audit replay trace

Your previous /app/replay now recovers correctly on the quirky samples. Ops wants visibility into what the replay actually did per crash site, not just the final heap.

Build an additional executable at /app/replay_audit with usage /app/replay_audit <crash-dir> <out-heap>. It must perform exactly the same recovery as /app/replay (same byte-exact output written to <out-heap>) and additionally update a cumulative audit file at /app/replay_audit.json.

Don't re-derive the page layout or record semantics from scratch — you already have the area and conventions from step 1. Reuse the replay logic you built.

The audit file /app/replay_audit.json must be valid JSON. Each run appends or merges an entry keyed by the crash-dir basename. Each entry must contain: pages_touched (int), records_applied (int, count of WAL records with lsn > pageLSN that actually affected a page), prunes_evaluated (int), prunes_fired (int, how many PRUNE records zeroed bytes because slot was dead under the same-lsn ordering you discovered), and checksum of output heap (simple file size + first 8 bytes of recovered output for sanity). If /app/replay_audit.json does not exist, create it with an object; if it exists, add/overwrite the key for this case.

Self-test: running /app/replay_audit over every /app/samples/caseNN into /tmp/audit_out_NN.bin must still produce byte-identical files to /app/samples/caseNN/recovered.bin, and /app/replay_audit.json must then contain one entry per case with records_applied matching the number you would get by applying the pageLSN filter and the bespoke intra-LSN order.

Body includes audit, replay, trace, /app/replay_audit, /app/replay_audit.json, /app/replay, /app/samples/, quirky.
