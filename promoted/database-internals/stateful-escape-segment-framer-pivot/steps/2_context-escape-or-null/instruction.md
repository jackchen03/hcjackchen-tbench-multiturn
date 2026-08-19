# Context escape or null

Your previous /app/framer matches the legacy framer on basic samples and on most random payloads, but it still fails when records contain a specific two-byte pattern. The new failure concentrates where a record payload has 0xAA followed by 0x00.

The transform must be reversible: a literal 0xAA 0x00 0x55 sequence in one record must not collide with an escaped 0xAA 0x55 marker from another. If you only escape 0xAA when the next byte is 0x55, the 0x00 case causes ambiguity, the escaped stream shifts, and every downstream block footer moves, making the whole segment byte-different.


Update the executable at /app/framer at the same path — it still reads stdin JSON {"records":[b64]} and writes raw segment on stdout byte-identical to legacy_framer. Keep writing raw bytes, no wrapper. Now it must also handle payloads containing 0xAA 0x00 correctly, not just 0xAA 0x55. For now it's okay if you still skip the empty final block case — that will be tackled next.

This step talks about escaping 0xAA followed by 0x00 — the body must mention /app/framer, /app/EDGE_PAYLOADS.json, /verifier/legacy_framer, 0xAA, 0x00, 0x55, and MAGIC.