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

DROP VIEW IF EXISTS case_v_gaps;
DROP VIEW IF EXISTS case_v_postings;
DROP VIEW IF EXISTS case_v_classified;
DROP VIEW IF EXISTS case_v_variants;
DROP TABLE IF EXISTS case_statement;
DROP TABLE IF EXISTS case_input;
DROP TABLE IF EXISTS case_cutoffs;

CREATE TABLE case_cutoffs (
    checkpoint VARCHAR(12) NOT NULL, cutoff_utc DATETIME NOT NULL
) DUPLICATE KEY(checkpoint) DISTRIBUTED BY HASH(checkpoint) BUCKETS 1
PROPERTIES ("replication_num"="1");
INSERT INTO case_cutoffs VALUES
    ('closed','2026-01-02 00:00:00'),('revised','2026-01-03 00:00:00');

CREATE TABLE case_input (
    delivery_id INT NOT NULL, event_key VARCHAR(8) NOT NULL, src_version INT NOT NULL,
    received_utc DATETIME NOT NULL, event_day DATE NOT NULL, merchant_id INT NOT NULL,
    currency CHAR(3) NOT NULL, entry_kind VARCHAR(12) NOT NULL, amount_minor BIGINT NOT NULL
) DUPLICATE KEY(delivery_id) DISTRIBUTED BY HASH(event_key) BUCKETS 2
PROPERTIES ("replication_num"="1");
INSERT INTO case_input VALUES
    (1,'A',1,'2026-01-01 09:01:00','2026-01-01',7,'USD','capture',1000),
    (2,'B',1,'2026-01-01 10:01:00','2026-01-01',8,'USD','capture',1400),
    (3,'B',1,'2026-01-01 10:02:00','2026-01-01',8,'USD','capture',1400),
    (4,'C',1,'2026-01-01 11:01:00','2026-01-01',7,'EUR','capture',500),
    (5,'R',1,'2026-01-01 13:01:00','2026-01-01',7,'USD','refund',300),
    (6,'Q',1,'2026-01-01 14:01:00','2026-01-01',8,'USD','capture',200),
    (7,'F',1,'2026-01-01 15:01:00','2026-01-01',8,'USD','failed',900),
    (8,'A',2,'2026-01-02 06:00:00','2026-01-01',7,'USD','capture',1200),
    (9,'A',2,'2026-01-02 06:05:00','2026-01-01',7,'USD','capture',1200),
    (10,'Q',2,'2026-01-02 07:00:00','2026-01-01',8,'USD','capture',250),
    (11,'Q',2,'2026-01-02 07:01:00','2026-01-01',8,'USD','capture',260),
    (12,'A',1,'2026-01-02 08:00:00','2026-01-01',7,'USD','capture',1000),
    (13,'N',1,'2026-01-02 10:01:00','2026-01-02',8,'USD','capture',800);

CREATE TABLE case_statement (
    checkpoint VARCHAR(12) NOT NULL, event_key VARCHAR(8) NOT NULL,
    merchant_id INT NOT NULL, currency CHAR(3) NOT NULL, entry_kind VARCHAR(12) NOT NULL,
    signed_minor BIGINT NOT NULL
) PRIMARY KEY(checkpoint,event_key) DISTRIBUTED BY HASH(event_key) BUCKETS 2
PROPERTIES ("replication_num"="1");
INSERT INTO case_statement VALUES
    ('closed','A',7,'USD','capture',1000),('closed','B',8,'USD','capture',1400),
    ('closed','C',7,'EUR','capture',500),('closed','R',7,'USD','refund',-300),
    ('closed','Q',8,'USD','capture',200),('revised','A',7,'USD','capture',1200),
    ('revised','B',8,'USD','capture',1400),('revised','C',7,'EUR','capture',500),
    ('revised','R',7,'USD','refund',-300),('revised','Q',8,'USD','capture',250);

CREATE VIEW case_v_variants AS
SELECT DISTINCT checkpoint,event_key,src_version,event_day,merchant_id,currency,entry_kind,amount_minor
FROM (
    SELECT c.checkpoint,i.*,DENSE_RANK() OVER (
        PARTITION BY c.checkpoint,i.event_key ORDER BY i.src_version DESC
    ) AS version_rank
    FROM case_cutoffs c JOIN case_input i ON i.received_utc<c.cutoff_utc
) ranked WHERE version_rank=1;

CREATE VIEW case_v_classified AS
SELECT v.*,COUNT(*) OVER (PARTITION BY checkpoint,event_key) AS variants
FROM case_v_variants v;

CREATE VIEW case_v_postings AS
SELECT checkpoint,event_key,merchant_id,currency,entry_kind,
       CASE WHEN entry_kind='refund' THEN -amount_minor ELSE amount_minor END AS signed_minor
FROM case_v_classified
WHERE variants=1 AND event_day='2026-01-01' AND entry_kind IN ('capture','refund');

CREATE VIEW case_v_gaps AS
SELECT COALESCE(a.checkpoint,s.checkpoint) AS checkpoint,
       COALESCE(a.event_key,s.event_key) AS event_key,
       CASE WHEN a.event_key IS NULL THEN 'missing_internal'
            WHEN s.event_key IS NULL THEN 'extra_internal' ELSE 'payload_mismatch' END AS reason,
       a.signed_minor AS internal_minor,s.signed_minor AS statement_minor
FROM case_v_postings a FULL OUTER JOIN case_statement s
  ON a.checkpoint=s.checkpoint AND a.event_key=s.event_key
WHERE a.event_key IS NULL OR s.event_key IS NULL OR a.currency<>s.currency
   OR a.entry_kind<>s.entry_kind OR a.merchant_id<>s.merchant_id OR a.signed_minor<>s.signed_minor;
