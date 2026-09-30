# PostgreSQL fixture

The live database contains `orders(customer_id int, status text,
created_at timestamptz, amount numeric)`.  `/app/schema.sql` is a replayable
schema migration; it must not assume a particular database name.

The sample has 50,000 rows. Grading uses fresh, isolated databases with at
least 500,000 rows. `/app/bounds.txt` is replaced by the verifier-owned fixed
budget for each fixture before candidate SQL runs.
