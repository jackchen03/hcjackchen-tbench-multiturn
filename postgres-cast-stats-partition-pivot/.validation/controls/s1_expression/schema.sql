CREATE INDEX orders_customer_expr_idx ON orders((customer_id::text));
ANALYZE orders;
