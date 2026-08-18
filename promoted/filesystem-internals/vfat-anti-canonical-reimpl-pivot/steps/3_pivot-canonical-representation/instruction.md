New evidence from hardware firmware validation shows the previous anti-canonical dialect wastes space and fails interoperability — real FAT stacks expect per-basis ~N collision, canonical slot count (len+12)/13, and NTRes case-bit handling. We must pivot to standard representation and drop the quirky code.

The previous quirks (global monotonic numeric tail that yields FILEON~1 / ALPHAT~2 / GAMMAS~3 for distinct basenames, always emitting LFN slots even for README.TXT and readme.txt with NTRes=0x00, and always-terminate packing that over-emits a slot when UTF-16 length % 13 == 0) must be removed.

Build a new executable /app/canonical_vfatdir used as canonical_vfatdir <names.txt> <out.bin> writing directory bytes in canonical VFAT form:

- Short-name collision uses per-basis smallest unused ~N (three distinct lossy names each get ~1)
- LFN slot count = (L+12)/13, terminator only if room, no extra slot at L%13==0
- Case optimization: if a name fits 8.3 and differs only by case, suppress LFN slots and set NTRes byte 0x0C to 0x08 base-lower, 0x10 ext-lower, 0x18 both; exact uppercase 8.3 gets no LFN either
- Basis derivation, invalid-char -> '_' replacement, space/dot dropping, 8/3 truncation to 8-len("~N"), standard LFN checksum sum = ((sum>>1)|(sum<<7))+byte over 11-byte name, UTF-16LE packing, 0x40 last-slot flag, reversed order remain canonical

Also output a cluster-chain manifest at /app/clusters.json: JSON object mapping each generated short name to its simulated cluster chain list (e.g., {"SHORT~1.TXT":[2,3,4]}) — use contiguous allocation starting at 2 incrementing per file, one cluster per file for simplicity, demonstrating shift from directory-byte-only to cluster-chain representation.

After this pivot, /app/myvfatdir and its global counter / always-LFN / always-terminate behavior must be absent — do not keep quirky formatter in final state. Tests will assert canonical_vfatdir matches standard behavior (per-basis tails, suppressed LFN, correct slot counts) and that /app/vfat_ls from prior step is no longer used with new format, and /app/canonical_vfatdir does NOT produce global ~1/~2/~3 for distinct basenames.
