# Byte-match the insert path's FSM page-selection dialect

You have a bulk loader that decides which heap page each tuple lands on. It does not simply append to the last page; it consults a free-space map summary that records how much free space each interior page has after deletes, reusing slack in the middle of the relation.

The old loader is still in the environment as a stripped binary at `/verifier/heapload`. You can run it to observe behavior: `/verifier/heapload <state_file>` reads a state file describing the current relation (pages, true free bytes, search cursor) and reads the batch to insert from stdin — one integer per line, the total byte size of that tuple — and prints the landing page id for each tuple to stdout, one per line, 0-based (new page id is current page count, increasing).

The state file format is inferable from examples under `/app/samples/` — look at `*.state`, `*.in`, `*.out`. It contains headers `USABLE`, `SLOT`, `CURSOR`, then number of pages and lines `<pid> <true_free>`. Your reimplementation with conventional "take first page whose recorded free >= size starting at block 0" mostly matches on uniform roomy batches, but diverges as soon as sizes are mixed near boundaries and when continuously filling interior pages.

Probe the reference binary with crafted states and batches to discover the real dialect: how free space is quantized into categories, where search starts, what happens when a selected page does not actually fit, how the search cursor changes between tuples, and when a new page is extended.

Deliver an executable at `/app/heapload` with identical usage: `/app/heapload <state_file>` reads state file and batch from stdin, prints landing page ids to stdout one per line.

Validation uses held-out states and batches disjoint from samples, including many mixed-size near-boundary cases and long runs that fill interior slack and force extends. Grading requires your landing sequence to be byte-for-byte identical to the reference. At grading time `/verifier/heapload` and `/app/samples` are removed, so your binary must be self-contained and must not call the old loader or hardcode sample outputs.
