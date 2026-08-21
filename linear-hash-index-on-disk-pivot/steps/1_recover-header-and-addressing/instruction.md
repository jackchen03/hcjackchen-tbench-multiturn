# Recover header and addressing for opaque linear-hash bucket file

We have a legacy primary hash index builder that reads a keyfile of integer primary keys and writes a disk bucket file `index.bin` used by an old engine for equality lookups. The colleague who wrote the format left, leaving only a stripped binary `/verifier/hashload`. We need a drop-in replacement.

The binary is still in this environment at `/verifier/hashload` — usage: `/verifier/hashload <keyfile> <output file>`. It writes the bucket file to the path you specify. Under `/app/samples/` there are example keyfiles and their corresponding `index.bin` outputs to compare. Input keyfile byte format is documented in `/app/KEYFILE.md`.

Your job for now is to focus on small keyfiles that do not trigger multi-page overflow split cascades. Use crafted keyfiles to feed the old tool and `hexdump -C`, `xxd`, `od -c` the outputs until you understand the on-disk layout: super-header fields, page capacity, slot layout and byte order, and how a key maps to a bucket number. The samples include `small_no_overflow.key` and `small_one_overflow.key` which are representative for this stage.

Place an executable at `/app/hashbuild` with same usage as the old tool: `/app/hashbuild <keyfile> <output file>` — read the keyfile, build the index, write it to output path. For this step, it must produce byte-for-byte identical output to `/verifier/hashload` on keyfiles that never force a bucket's overflow chain length to reach 2 or more, i.e., at most one overflow page per bucket and no split cascade. We will test it on held-out small keyfiles with unseen keys while `/verifier/hashload` is still present for probing, but your binary must be self-contained and not call the oracle at runtime.

Do not pre-create files that belong to later steps.
