Your previous /app/myvfatdir now produces byte-exact directory bytes matching the opaque reference at /app/reference/vfatdir. Using that exact format, add a recovery/listing tool that relies on it — do not re-explain the formatter.

Build an executable /app/vfat_ls used as vfat_ls <dir.bin> that reads raw directory bytes (as produced by /app/myvfatdir) and prints the long filenames to stdout, one UTF-8 name per line, in the original insertion order preserved by dir.bin.

It must correctly parse the quirky dialect you just reimplemented: every name has LFN slots even when it fits 8.3 (NTRes byte at offset 0x0C is always 0x00, no case-suppression), LFN slot count uses always-append 0x0000 terminator then 0xFFFF pad (so it over-emits one slot when UTF-16 length % 13 == 0), checksum is standard ((sum>>1)|(sum<<7)) + byte over final 11-byte short name, slots have 0x40 last-flag, order reversed. The tool will be tested by generating dir.bin via /app/myvfatdir on held-out lists, then running /app/vfat_ls <dir.bin> and comparing stdout lines to the original names.txt. Round-trip must be exact.

Keep /app/myvfatdir working — tests reuse it to generate inputs for /app/vfat_ls.
