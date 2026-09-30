The dashboard query in /app/query.sql takes minutes on the database described by /app/schema.sql, though the tables look small and the same query flies on a colleague's machine. Something beneath the surface is off. Run any customer lookup as `/app/run_query.sh <customer_id>`, which feeds the id into /app/query.sql.

Make the query fast on this database without changing what it returns. The graded
database is at least ten times the sample size: any plan is accepted as long as it
never sequentially scans the orders table, keeps its total shared-buffer use under
the budget number in /app/bounds.txt, and returns the exact rows. Check yourself
with `EXPLAIN (ANALYZE, BUFFERS)` on your lookup: sum hit+read over all plan nodes
and compare against /app/bounds.txt, which the harness stages per database with a
fixed verifier-owned number. Padding the tables or flipping planner switches
without lowering that buffer sum is not a fix. Keep /app/query.sql as the query and
/app/schema.sql as the schema. More steps follow; conserve resources.
