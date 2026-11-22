DROP TABLE IF EXISTS demo_deliveries;
CREATE TABLE demo_deliveries (
    delivery_id INT NOT NULL,
    event_id INT NOT NULL,
    merchant_id INT NOT NULL,
    event_kind VARCHAR(12) NOT NULL,
    currency CHAR(3) NOT NULL,
    amount_minor BIGINT NOT NULL
) DUPLICATE KEY(delivery_id)
DISTRIBUTED BY HASH(event_id) BUCKETS 2
PROPERTIES ("replication_num"="1");
INSERT INTO demo_deliveries VALUES
    (1,101,7,'captured','USD',1200), (2,102,8,'captured','USD',1200),
    (3,101,7,'captured','USD',1200), (4,103,7,'captured','USD',900),
    (5,104,8,'captured','EUR',500), (6,105,8,'failed','USD',2000),
    (7,106,7,'refunded','USD',300);
