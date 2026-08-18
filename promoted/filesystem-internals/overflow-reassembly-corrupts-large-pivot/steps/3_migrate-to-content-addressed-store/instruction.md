The per-row recovery you built works, but downstream now wants deduplicated, content-addressed storage. Storing files as `<rowid>.bin` couples identity to rowid and duplicates identical content — backups are growing fast.

Switch the layout to content-addressed. Your previous step's output in /app/recovered/ must be migrated and then removed because downstream now assumes only the new layout exists.

Requirements:

- Read each file you previously recovered (the byte-exact BLOBs) and compute its SHA-256. Hex encode in lowercase.
- Write deduplicated blobs under /app/store/ — one file per unique content, named `<sha256>.bin` (e.g. `e3b0c44298fc...bin`).
- Write a manifest /app/manifest.json mapping each original rowid (as string) to its sha256 hex string, e.g. `{"1":"ab12...", "2":"cd34..."}`. Must be valid JSON and include every row id from before.
- After migration is verified, remove the old /app/recovered/ directory entirely — it must not exist after this step. Downstream will fail if both layouts are present.

This step must preserve byte exactness: if your earlier recovery had silently corrupted large blobs, the hashes here would be wrong and downstream verification will catch it.

You already have /app/recovered/ and your generic carver /app/recover.sh from last step; reuse their exact byte outputs to build the new layout.
