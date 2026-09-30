CREATE INDEX orders_customer_cover_idx
 ON orders(customer_id) INCLUDE(status,created_at,amount);
CREATE INDEX orders_created_at_idx ON orders(created_at);
VACUUM (ANALYZE) orders;
