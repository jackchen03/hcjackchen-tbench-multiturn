# Add split trigger and overflow chain handling

Your previous `/app/hashbuild` passes small keyfiles but fails when keys are enough to trigger multiple splits and multi-page overflow chains — outputs diverge in bucket count, level, split pointer and page bytes.

The old engine's split logic is not textbook load-factor; probing the oracle with colliding keyfiles that pile onto one bucket shows splits correlate with overflow-chain length, not total occupancy. Also overflow pages are chained newest-first, not appended at tail.

Extend the same `/app/hashbuild` executable (same path, same `<keyfile> <out>` usage) so it now handles larger keyfiles that force several splits and fill overflow chains. It must produce byte-for-byte identical files to `/verifier/hashload` for keyfiles that trigger multiple splits and multi-page chains.

Do not repeat header, page capacity, slot layout or addressing discovery from step1 — you already have those conventions from `/app/KEYFILE.md` and your prior binary.

As part of this step, also write `/app/chain_discovery.txt` containing two lines: first line `threshold=<int>` is the chain-length threshold T you discovered that triggers a split, second line `direction=<newest-first|newest-last>` is the overflow chaining direction you observed. Use exactly those keys and lowercase values. This file proves you probed the quirk; its exact format will be checked.

Keep `/app/hashbuild` self-contained; it must not call `/verifier/hashload` at runtime.
