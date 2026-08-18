Factors look good on the held-out sample now.

Training wants visibility into which entities were hit by the writer upgrade bug. Build a report at /app/out/drift_report.json that captures every entity where taking the last occurrence in the file would have picked a stale vector.

The report must be JSON with keys: num_reordered_users, num_reordered_items, reordered: list of objects each with type ("user" or "item"), id (int logical id), max_step (int, the step you actually kept), stale_step (int, step of the row sitting at last file position). Sort the reordered list by type then id. Counts must match the list.

Don't redo the factor files — keep the restored checkpoint as is.
