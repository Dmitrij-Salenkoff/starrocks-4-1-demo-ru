DROP TABLE IF EXISTS cafe_sales;
CREATE TABLE cafe_sales (
    receipt_id INT NOT NULL,
    sale_day DATE NOT NULL,
    coffee VARCHAR(16) NOT NULL,
    cups INT NOT NULL
)
PRIMARY KEY (receipt_id)
DISTRIBUTED BY HASH(receipt_id) BUCKETS 1
PROPERTIES ("replication_num" = "1");

INSERT INTO cafe_sales (receipt_id, sale_day, coffee, cups) VALUES
    (100, '2026-01-02', 'espresso', 4),
    (101, '2026-01-03', 'latte', 2),
    (102, '2026-01-03', 'espresso', 1),
    (103, '2026-01-03', 'latte', 3);
