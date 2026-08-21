# Mandatory tail pivot

Your escape fix from last step clears payloads with 0xAA 0x00 but still fails some segments. Fresh evidence: segments whose escaped logical length lands exactly on a block boundary still fail verification. Previous framer treated "no remainder" as "no tail" and omitted the final block, but the legacy framer always emits it.

Check /app/BOUNDARY_CASES.json and /app/PROFILING.md — they contain batches where len(E) mod 16 == 0 and show the expected tail is a footer with bytes 0x11 0x1F followed by a LEB128 varint 0x00. The old path that checked `if rem == 0: skip` is wrong. The reference dialect always emits a partial-final block even when rem == 0, with its Fletcher-16 footer being the raw init and varint counting escaped bytes as 0, and any unconditional escaping of 0xAA (escaping every 0xAA regardless of next byte) over-escapes and must be removed.

Switch to mandatory final block handling. For any escaped stream length, emit the remaining bytes plus their footer, then LEB128 varint of rem, always — even when rem == 0, the footer is 0x11 0x1F and varint is 0x00. Keep the conditional look-ahead escape only when 0xAA is followed by 0x55 or 0x00, not unconditionally.

Remove the old logic. The previous path that escaped 0xAA unconditionally without checking next byte must go — it over-escapes and shifts block boundaries. The path that skipped the final block when rem == 0 must go — it drops 3 bytes and breaks boundary scan. The final /app/framer must not contain those branches.

Keep the same command /app/framer reading {"records":[b64]} from stdin and writing raw segment to stdout, same as before. Read /app/PROFILING.md and /app/BOUNDARY_CASES.json for the mandatory tail contract and use /app/samples/ and /app/EDGE_PAYLOADS.json for regression. You need 0xAA, 0x55, 0x00, 0x11, 0x1F, LEB128, /app/framer, /verifier/legacy_framer, /app/BOUNDARY_CASES.json, /app/PROFILING.md all together.

This step is about mandatory tail pivot — body includes mandatory, final block, rem==0, empty, unconditional, /app/BOUNDARY_CASES.json, /app/PROFILING.md, 0x11, 0x1F, LEB128, /app/framer.
This step must handle rem==0 footer correctly.
