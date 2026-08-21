# Fix cross-shard centering and add validation relying on carried layout

Your previous repair made `/app/embstore/primary_002.bin` byte-complete and crc-valid, but held-out recall is still RED because the recovered rows you copied verbatim are stored under different mean-centering: replica shards store `true_vec - replica_mean` while primary shards serve `row + means[primary_shard]`. A verbatim byte copy offsets each recovered vector by `means[replica_shard] - means[002]`.

Fix the offset: for each recovered id you located via back-pointer inversion, read the replica row as float32, un-center it by adding `means[replica_shard]` from ``, then re-center for primary shard 002 by subtracting `means[002]`. Write the result as float16 into the correct row slot of `primary_002.bin` and recompute crc32.

Then add a validation script at `/app/embstore/validate_integrity.py` that relies on the carried file layout you just fixed. The script must: parse `meta.json`, ``, ``, verify each primary and replica shard's expected byte length vs actual and crc32 per `FORMAT.md`, enumerate lost ids via `` tail, invert replica `backptr_table` to check each recovered row reconstructs within 1e-2 of true space after correct re-centering formula `primary_row + means[002] == replica_row + means[replica_shard]`, and run a small recall check via `load_store` + `topk` on samples under `/app/samples/` if present.

Keep using `/app/embstore/` same file, same loader `load_store`/`topk` in `embstore_lib.py`, same layout from `FORMAT.md`. Do not yet pivot to flat layout.

Title keywords: recenter, validate, integrity.