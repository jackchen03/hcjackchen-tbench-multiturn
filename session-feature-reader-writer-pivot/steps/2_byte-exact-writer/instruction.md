That reader unblocks inspection, but we also need to produce new shards that serving will accept.

Extend the same module at /app/session_codec.py to also expose encode_shard(sessions, out_path) — given a list of sessions in the same structure your reader returns, write a shard file to out_path that is byte-identical to what the canonical writer would produce for those sessions, is accepted by /app/session_serving_validate with exit code 0, and round-trips through your own decode_shard exactly back to the input sessions. The file layout must satisfy serving's alignment and checksum rules that the validator checks. Do not modify the validator or sample shards. Grading will use held-out sessions with values disjoint from the samples, comparing your bytes to the reference writer and checking serving acceptance plus round-trip.

Title keywords session, feature, writer must appear.
