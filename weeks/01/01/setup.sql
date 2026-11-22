DROP TABLE IF EXISTS sr_date_tenant;
DROP TABLE IF EXISTS sr_event_hash;
CREATE TABLE sr_date_tenant (
    event_day DATE NOT NULL, tenant_id INT NOT NULL, event_id INT NOT NULL, cents INT NOT NULL
) DUPLICATE KEY(event_day,tenant_id,event_id)
PARTITION BY RANGE(event_day) (
    PARTITION p01 VALUES LESS THAN ("2026-01-02"),
    PARTITION p02 VALUES LESS THAN ("2026-01-03"),
    PARTITION p03 VALUES LESS THAN ("2026-01-04"),
    PARTITION p04 VALUES LESS THAN ("2026-01-05")
)
DISTRIBUTED BY HASH(tenant_id) BUCKETS 4 PROPERTIES ("replication_num"="1");
CREATE TABLE sr_event_hash (
    event_day DATE NOT NULL, tenant_id INT NOT NULL, event_id INT NOT NULL, cents INT NOT NULL
) DUPLICATE KEY(event_day,tenant_id,event_id)
DISTRIBUTED BY HASH(event_id) BUCKETS 16 PROPERTIES ("replication_num"="1");
INSERT INTO sr_date_tenant
SELECT CASE WHEN generate_series<32768 THEN CAST('2026-01-01' AS DATE)
            WHEN generate_series<65536 THEN CAST('2026-01-02' AS DATE)
            WHEN generate_series<98304 THEN CAST('2026-01-03' AS DATE)
            ELSE CAST('2026-01-04' AS DATE) END,
       MOD(generate_series,128),generate_series,100+MOD(generate_series,1000)
FROM TABLE(generate_series(0,131071));
INSERT INTO sr_event_hash SELECT event_day,tenant_id,event_id,cents FROM sr_date_tenant;
