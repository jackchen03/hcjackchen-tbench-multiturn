# Detect reuse via generation

Your previous /app/recover passes checksum and length but still lands wrong bytes in the middle of some values. Those slots were reused — they now hold foreign data even though the chunk looks valid.

Reused slots still give wrong bytes — figure out how to know a slot no longer belongs to this value and where to get the real bytes. Don't re-derive the chain layout from scratch; you already have the area and conventions.

You have alloc.map now in addition to overflow.store and lob.dir. Each chain reference keeps expected_gen and each alloc entry keeps current_gen. Use that disagreement to detect a reused slot. For now any fix that replaces the foreign window with the right original bytes is okay, even if you key the replacement on owner. Keep /app/recover at the same path and keep writing <value_id>.bin files with value_id naming.

This step talks about detecting reuse via generation — the body must mention expected_gen, current_gen, alloc.map, overflow.store, lob.dir.
The output for this step must include /app/alloc.map.
The output for this step must include /app/undo.log.