Growth killed that approach: once history dominates, the hot-window report scans the
full history no matter how we tune the point lookup. The new partitioned layout is
described in /app/growth/layout.sql, which appears from this step on, including the
fixed hot-cutoff date the layout and the data are anchored to.

Move the hot path off the history table onto that layout: put the hot-window query
(all orders with created_at on or after the cutoff, ordered by created_at ascending)
in /app/hot_query.sql, run as `psql -f /app/hot_query.sql`. Hot-window results must
match exactly as multisets in that order; the hot query must prune the history
partition (EXPLAIN shows no scan node on orders_hist) and must stay under the hot
budget number in /app/bounds.txt. Point lookups through /app/run_query.sh keep
working with exact rows for hot ids. Stop sorting or scanning the full history.
