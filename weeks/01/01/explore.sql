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

SELECT delivery_id,event_key,src_version,received_utc,amount_minor
FROM case_input WHERE event_key IN ('A','Q') ORDER BY event_key,received_utc;
SELECT checkpoint,event_key,src_version,amount_minor,variants
FROM case_v_classified WHERE event_key IN ('A','Q') ORDER BY checkpoint,event_key,amount_minor;
SELECT checkpoint,currency,
       SUM(CASE WHEN entry_kind='capture' THEN signed_minor ELSE 0 END) AS gross_captures,
       SUM(CASE WHEN entry_kind='refund' THEN -signed_minor ELSE 0 END) AS refunds,
       SUM(signed_minor) AS net_minor,COUNT(*) AS entries
FROM case_v_postings GROUP BY checkpoint,currency ORDER BY checkpoint,currency;
SELECT checkpoint,event_key,reason,internal_minor,statement_minor
FROM case_v_gaps ORDER BY checkpoint,event_key;
