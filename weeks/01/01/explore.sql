SHOW FRONTENDS;
SHOW BACKENDS;
SELECT delivery_id, event_id, merchant_id, event_kind, currency, amount_minor
FROM demo_deliveries ORDER BY delivery_id;
SELECT SUM(amount_minor) AS reported_minor
FROM demo_deliveries WHERE event_kind='captured' AND currency='USD';
SELECT event_id, COUNT(*) AS copies, MIN(amount_minor) AS low_minor, MAX(amount_minor) AS high_minor
FROM demo_deliveries WHERE event_kind='captured' AND currency='USD'
GROUP BY event_id ORDER BY event_id;
WITH ranked AS (
    SELECT d.*, ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY delivery_id DESC) AS rn
    FROM demo_deliveries AS d
)
SELECT COUNT(*) AS captures, SUM(amount_minor) AS gross_minor
FROM ranked WHERE rn=1 AND event_kind='captured' AND currency='USD';
EXPLAIN SELECT event_id, COUNT(*)
FROM demo_deliveries WHERE event_kind='captured' AND currency='USD' GROUP BY event_id;
