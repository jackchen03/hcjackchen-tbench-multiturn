Firmware validation just failed — the nonstandard journal dialect you reimplemented is incompatible with the upstream kernel. Real hardware expects canonical jbd2, so your previous reimpl must be dropped for production.

This is a pivot: switch to a canonical jbd2 recovery implementation and drop all the nonstandard quirks you added. The new binary is at /app/canonical_recover with CLI canonical_recover <base image> <journal file> <output image>. It must implement standard jbd2 semantics, not the oracle's:

- revoke comparator is >= : if a data block is written and revoked in the same transaction (revoke_seq == S), it is dropped (the opposite of the oracle's strict > rule that kept it)
- escape sentinel is the journal magic 0xc03b3998 : on replay, an escaped block's first 4 bytes are restored to 0xc03b3998, not the oracle's different word
- descriptor tag geometry is standard jbd2 (no forced inline 16-byte UUID on first tag, no conditional SAME_UUID re-inline based on byte-match; standard tag packing and UUID handling)
- commit validity uses standard crc32c seed and standard byte range (not the oracle's nonstandard seed/range that included descriptor tags and excluded trailing UUIDs)

Additionally, your canonical tool must be able to audit its view of commits. When you run /app/canonical_recover, have it also write /app/canonical_report.json (or provide a companion tool that writes it) containing "committed" sorted list under standard checksum validation, same JSON shape as before: {"committed":[...]}. The graded journals for canonical will include cases where standard vs nonstandard committed sets differ.

Absence requirement: /app/canonical_recover must NOT keep same-transaction revoked blocks, must NOT restore the oracle's non-magic sentinel, must NOT parse tags with conditional inline-UUID rule, and must NOT use the oracle's nonstandard crc32c seed. The verifier will test that distinct behaviour differs from /app/myrecover — e.g., a journal that revokes a block in its own txn must produce different recovered images between /app/myrecover (keeps) and /app/canonical_recover (drops), and an escaped block must contain 0xc03b3998 after canonical replay, not the oracle word. You should remove or rewrite the quirky codepath; keeping both behaviours in one binary violates the pivot.

Output contract: /app/canonical_recover <base image> <journal file> <output image> byte-exact under canonical rules, and /app/canonical_report.json exists with committed list. The title keywords nonstandard journal reimpl pivot describe this shift.
