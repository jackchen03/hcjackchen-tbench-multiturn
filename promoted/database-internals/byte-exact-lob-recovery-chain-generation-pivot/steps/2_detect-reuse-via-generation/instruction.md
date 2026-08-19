# Detect reuse via generation

Your previous /app/recover passes checksum and length but still lands wrong bytes in the middle of some values. Those slots were reused — they now hold foreign data even though the chunk looks valid.

Reused slots still give wrong bytes — figure out how to know a slot no longer belongs to this value. Don't re-derive the chain layout from scratch; you already have the area and conventions.

You have alloc.map now in addition to overflow.store and lob.dir. Each chain reference keeps expected_gen and each alloc entry keeps current_gen. Use that disagreement to detect a reused slot. For this step, only handle detection — do NOT attempt to replace foreign bytes with original bytes yet; recovery of original bytes will be tested only later. Keep /app/recover at the same path and keep writing <value_id>.bin files with value_id naming (recovery may still be imperfect until next step).

This step talks about detecting reuse via generation — the body must mention expected_gen, current_gen, alloc.map, overflow.store, lob.dir.
The output for this step must include /app/alloc.map.
The output for this step must include /app/2_reuse_detected.json.

Write a detection report to /app/2_reuse_detected.json listing reused slots where expected_gen != current_gen. The JSON should be an array of objects each with at least slot_index, expected_gen, current_gen, or a map from value_id to list of reused slot indices. Detection must be based on expected_gen != current_gen comparison.