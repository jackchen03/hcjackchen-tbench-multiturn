CREATE INDEX orders_customer_composite_idx ON orders(customer_id, created_at);
ANALYZE orders;
