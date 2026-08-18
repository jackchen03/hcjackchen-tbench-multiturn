Now that you have a byte-exact replayer, we need to understand what it actually committed, revoked, and escaped.

The nonstandard dialect you just reversed is load-bearing for this audit — tag stride, conditional inline UUID, escape handling, and commit validation all affect which transactions count and which blocks are kept.

Build a tool at /app/journal_audit with CLI journal_audit <journal file> <report json>. When run on any .jnl file, it must parse the journal ring and write /app/journal_report.json (and also to the <report json> path you are given) containing committed, revoked, and escaped state:

- committed: sorted list of transaction sequence numbers considered committed under the oracle's checksum rule (crc32c with its nonstandard seed and byte range that includes descriptor tags but excludes trailing UUIDs)
- revokes: object mapping block number as decimal string to max revoke sequence among committed transactions, e.g. {"128":"5"}
- escaped: sorted list of objects each {"seq": <int>, "blocknr": <int>, "txn_offset": <int>} for every data block in committed transactions that was escaped (its first 4 bytes originally equaled the oracle's non-magic sentinel, not 0xc03b3998), ordered by seq then blocknr

The audit must use the exact same parsing you used for /app/myrecover: first tag of each transaction always carries an inline 16-byte UUID, and SAME_UUID suppression on later tags only applies when it byte-matches the first; revoke decision is strict > (a block revoked in its own transaction is kept); escaped blocks must report the oracle sentinel word restoration point, not 0xc03b3998; commit validity uses the oracle's seed/range. Run it on your samples and compare to what /app/myrecover does internally — they should agree.

Sample check: running /app/journal_audit /app/samples/journal-1.jnl /app/journal_report.json should produce valid JSON with the keys above.
