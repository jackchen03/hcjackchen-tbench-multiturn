Now we also need to produce new files in the exact same opaque format so downstream can consume them.

Extend the same /app/seen_reader.py module you already have to also expose write_served_items(path, item_ids). It takes a file path to write and an iterable of ints (item ids) and must write a file that your read_served_items from step 1 can read back to the exact same set, and that remains valid under the real format.

The output for this step must include /app/seen_reader.py:write_served_items.
The output for this step must include /app/seen_reader.py:iter_served_items.
Additionally, write a short JSON report of what you fixed to /app/2_roundtrip_writer_metrics.json.
