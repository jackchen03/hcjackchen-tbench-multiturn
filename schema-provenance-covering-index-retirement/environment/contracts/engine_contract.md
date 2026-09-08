# Catalog engine contract

Invoke `/app/bin/run_scenario.py` with JSON Lines on stdin. It emits one deterministic JSON object per input line. Malformed input emits `{"error":"invalid_scenario"}` and exits nonzero.

Each scenario supplies `schemas` (schema ID to ordered field names), `pages` (ID, materializing schema, and logical rows), alias mutations, requested covering reads, and optionally a typed metadata graph. A covering read must equal the heap value for the requested page, key, field order, and snapshot. This remains true for pages created before later aliases, split/merge/cycle mutations, and compactions.

Diagnostics expose `witnesses`, `projection_steps`, `heap_fallbacks`, and `reindexes`. A page read at projection width `w` may expose at most `2*w+6` distinct witness nodes. For one scenario, `projection_steps <= 24*pages_touched + 16*alias_mutations + 128`; heap fallback and reindex counters remain zero.

Metadata nodes have typed directed dependencies (`alias`, `manifest`, `page`, `capsule`, `continuation`). Retirement retains the least dependency-closed set reachable from current roots, roots of open snapshots, and post-migration continuation roots. Its `roots` entries use authority labels `current`, `snapshot:<snapshot-id>`, and `continuation:<continuation-id>`. Each non-root `paths` entry has `id` and a nonempty `path`; every path element has `src`, `dst`, and `kind`. Any valid typed path from an authoritative root is accepted. Output ordering is lexical and deterministic.

Continuation migration atomically replaces that continuation's roots; open snapshots retain their own roots until close. For `r` changed roots, `e` changed edges, and `c` migrated continuations, additional `maintenance_steps <= 40*(r+e+c)+256`, independent of total graph size. A no-change retirement adds at most 32.
