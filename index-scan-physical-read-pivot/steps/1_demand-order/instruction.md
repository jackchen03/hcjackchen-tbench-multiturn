Our storage engine has a B+ tree range scan operator. The prefetch logic was lost and only a stripped binary remains at `/app/scan`. It can still emit the correct physical page read trace for any input.

For this first milestone, recover only the demand-read order. The fixture is a static B+ tree file, layout documented in `/app/FORMAT.md` — page 0 meta header with root page id, internal pages with separator keys and child page ids, leaf pages with sorted keys plus `next_sibling` physical page id. Leaf key order is NOT physical page id order; leaves are scattered.

The scan is defined by key interval `[lo, hi]` and a warm pool file listing physical pages already resident in the buffer pool (newline-separated decimal ids in `<warmpool_file>`). Demand reads walk from root down to the leftmost leaf covering `lo`, then follow `next_sibling` pointers in key order until a leaf's min key > `hi`. Each visited leaf that is not already resident and not already seen would issue a physical read.

Build an executable at `/app/scan_demand` with usage `/app/scan_demand <fixture> <lo> <hi> <warmpool_file> <out_file>`. It must parse the fixture per `/app/FORMAT.md`, perform the demand walk described, and write to `<out_file>` one physical page id per line, decimal integer, in the exact demand issue order, suppressing reads for pages listed in `<warmpool_file>` (and suppressing re-reads of already emitted pages). No extra content, no prefetch reads yet.

Sample demand-only traces are under `/app/samples/demand/` with disjoint values from held-out. We will test with different fixtures and disjoint `(range, warmpool)` inputs, so parse generically, don't hardcode.

More steps follow; conserve resources.
