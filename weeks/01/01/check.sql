SELECT IF(SUM(original_receipt) = 4 AND COUNT(*) = 4 + SUM(extra_receipt), 1, 0) AS ok
FROM (
    SELECT
        CASE
            WHEN receipt_id = 100 AND sale_day = '2026-01-02' AND coffee = 'espresso' AND cups = 4 THEN 1
            WHEN receipt_id = 101 AND sale_day = '2026-01-03' AND coffee = 'latte' AND cups = 2 THEN 1
            WHEN receipt_id = 102 AND sale_day = '2026-01-03' AND coffee = 'espresso' AND cups = 1 THEN 1
            WHEN receipt_id = 103 AND sale_day = '2026-01-03' AND coffee = 'latte' AND cups = 3 THEN 1
            ELSE 0
        END AS original_receipt,
        CASE
            WHEN receipt_id = 104 AND sale_day = '2026-01-03' AND coffee = 'espresso' AND cups = 2 THEN 1
            ELSE 0
        END AS extra_receipt
    FROM cafe_sales
) checked_receipts;
