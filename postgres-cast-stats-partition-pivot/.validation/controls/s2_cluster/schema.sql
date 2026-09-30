CREATE INDEX orders_customer_cluster_idx ON orders(customer_id);
CLUSTER orders USING orders_customer_cluster_idx;
VACUUM (ANALYZE) orders;
