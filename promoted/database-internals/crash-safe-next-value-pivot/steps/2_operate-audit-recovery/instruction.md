Your /app/recover from step 1 now fixes the collision by recovering the crash-safe next value.

Ops now needs the second half of the original outage: the audit list of "which ids were really used committed" is still inconsistent with table data — it over-counts aborted and in-progress ids and also includes burned tails.

Extend the same /app/recover binary — keep its existing <input_dir> <output_file> contract and its byte layout parsing, keep next value logic unchanged. Now it must also compute committed_consumed: set of values where INSERT(xid, seq_id, value) in WAL and xid has a COMMIT record, excluding ABORTed and in-progress (no COMMIT and no ABORT). Sorted integer ascending per sequence.

Change output format to name|next|committed_csv per line, sorted by name, csv comma-separated without spaces ascending, empty field if none, newline terminated. Keep decimal next handling.

We will run your binary on held-out fixtures (disjoint names/ranges, includes aborted top-of-block ids, in-progress txn, descending, cycle crossing, zero REFILL) and check exact byte equality. Also verify adaptation to prior step: next values must still equal your step 1 output for same pre-crash fixtures before post-crash work, and committed set must exclude aborted/in-progress.

Use carried conventions and files from previous step; don't re-derive FORMATS.md or seqcat/ckpt paths from scratch.
