Your ASCII-only dirhash now matches the oracle on ASCII names, but the batch we need to place contains filenames with raw bytes >= 0x80 (non-UTF8) and those still mismatch on the second hash word.

Extend the same `/usr/local/bin/dirhash` binary to handle the full byte range. Keep the calling convention `dirhash <seed_hex> <filename>` and the output format `"%08x %08x"` major minor from step 1; both words must now match the oracle for any byte value 0x00-0xFF except embedded NUL.

Probe the oracle with high-bit bytes to see where major stays matching while minor diverges. No new files are required, just fix the existing binary to cover both words correctly across seeds with different low bits.
