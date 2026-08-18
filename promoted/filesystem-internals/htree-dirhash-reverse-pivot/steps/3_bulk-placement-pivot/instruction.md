Fork-execing your per-file dirhash for 100k filenames is too slow on the placement pipeline traces we just profiled — lookups dominate and the process creation cost is the bottleneck. Switch to a bulk interface.

Build `/usr/local/bin/dirhash-bulk` that reads a seed on the first line of a file, then newline-delimited filenames. Contract: `dirhash-bulk <seed_hex> <names_file>` where `names_file` may contain any byte except NUL and newline as filename (raw bytes preserved). It must write `/app/buckets.json` as a JSON object mapping major hash (8-char lower hex) to sorted list of filenames from the input that hash to that major (sort lexicographically by raw byte value, UTF-8 decode with surrogateescape). No per-file stdout. Exit 0 on success.

As part of this pivot, the old per-file binary at `/usr/local/bin/dirhash` and the oracle at `/usr/local/bin/dirhash-oracle` must be absent after step 3 finishes — this step replaces the single-file CLI workflow.

More steps follow this optimization; conserve container resources.
