CREATE DATABASE IF NOT EXISTS sr01;
USE sr01;

DROP VIEW IF EXISTS daily_revenue;
DROP TABLE IF EXISTS payment_events;

CREATE TABLE payment_events (
    event_id BIGINT NOT NULL,
    event_day DATE NOT NULL,
    order_id BIGINT NOT NULL,
    event_type VARCHAR(12) NOT NULL,
    amount_minor BIGINT NOT NULL
)
DUPLICATE KEY (event_id)
DISTRIBUTED BY HASH (event_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

INSERT INTO payment_events VALUES
    (1, '2026-01-12', 501, 'capture', 12000),
    (2, '2026-01-12', 502, 'capture',  8000),
    (3, '2026-01-12', 503, 'decline',  4500),
    (4, '2026-01-12', 501, 'refund',   2000),
    (5, '2026-01-13', 504, 'capture',  6000),
    (6, '2026-01-13', 502, 'refund',   8000),
    (7, '2026-01-14', 505, 'decline',  3000);

CREATE VIEW daily_revenue AS
SELECT event_day, CAST(0 AS BIGINT) AS capture_count,
       CAST(0 AS BIGINT) AS gross_minor, CAST(0 AS BIGINT) AS refund_minor,
       CAST(0 AS BIGINT) AS net_minor
FROM payment_events
WHERE 1 = 0;
