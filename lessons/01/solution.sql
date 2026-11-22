USE sr01;

CREATE OR REPLACE VIEW daily_revenue AS
SELECT event_day, capture_count, gross_minor, refund_minor,
       gross_minor - refund_minor AS net_minor
FROM (
    SELECT event_day,
           SUM(CASE WHEN event_type = 'capture' THEN 1 ELSE 0 END) AS capture_count,
           SUM(CASE WHEN event_type = 'capture' THEN amount_minor ELSE 0 END) AS gross_minor,
           SUM(CASE WHEN event_type = 'refund' THEN amount_minor ELSE 0 END) AS refund_minor
    FROM payment_events
    GROUP BY event_day
) AS daily;
