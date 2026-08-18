We found more evidence from the same incident.

There's a second carved leaf page from the same family at /app/case2/second.page with its own schema at /app/case2/schema.sql. It's the same kind of bare leaf page, different table and values.

Extend your carver so it can handle this new case without breaking the first one. It should still work on /app/case/ via /app/carve.sh, but now also produce a merged view: decode both pages, union the rows de-duplicated by primary key (last wins), sorted by primary key ascending, same pipe format, into /app/merged.txt (and /workdir/merged.txt if that dir exists).

Don't re-explain the page layout — reuse what you built in step 1. The second table also has the same quirks (non-first primary key, decoy NULLs, small integers before a large one) but at different positions and with different column names. If your step 1 was hardcoded to the first table, this step will catch it.
