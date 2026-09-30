CREATE TEMP TABLE inserted_tids (tid tid);
WITH inserted AS (
  INSERT INTO orders SELECT * FROM orders LIMIT 100000
  RETURNING ctid
)
INSERT INTO inserted_tids SELECT ctid FROM inserted;
DELETE FROM orders o USING inserted_tids i WHERE o.ctid = i.tid;
ANALYZE orders;
