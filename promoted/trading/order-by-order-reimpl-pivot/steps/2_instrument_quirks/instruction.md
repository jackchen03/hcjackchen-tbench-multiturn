Your rebuilder from the previous step now matches the legacy binary and is running in shadow.

We need visibility into how often its unusual branches fire. Extend it so that on each run, in addition to printing the snapshot to stdout (contract from step1 still must hold byte-identical), it also writes a JSON summary to `/app/quirks_report.json`.

The JSON should contain exactly these keys:
- `retained_zero_count`: number of orders that remain in the book with displayed size 0 after an execution and still appear as `ref:0` in the snapshot
- `replace_keep_priority_count`: number of Replace `U` messages where the order kept its previous queue position (priority kept)
- `replace_lose_priority_count`: number of Replace `U` where it moved to tail (priority lost)
- `rekeyed_refs`: sorted list of new reference numbers introduced by Replace that kept priority in place (those re-keyed without moving)

Keep the stdout snapshot identical to before — we still validate it byte-for-byte against the quirky reference. The new file `/app/quirks_report.json` will be checked for correct counts on held-out feeds.
