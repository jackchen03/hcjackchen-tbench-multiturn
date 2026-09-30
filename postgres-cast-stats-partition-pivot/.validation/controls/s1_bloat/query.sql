SELECT customer_id, status, created_at, amount
FROM orders
WHERE customer_id::text = :'cid'
ORDER BY created_at, status, amount;
