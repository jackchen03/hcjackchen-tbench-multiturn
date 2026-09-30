CREATE INDEX orders_skew_partial_idx ON orders(customer_id)
WHERE customer_id >= 910001;
VACUUM (ANALYZE) orders;
