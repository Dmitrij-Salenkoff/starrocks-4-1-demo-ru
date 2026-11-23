SELECT coffee, COUNT(*) AS receipts, SUM(cups) AS cups
FROM cafe_sales
WHERE sale_day = '2026-01-03'
GROUP BY coffee
ORDER BY coffee;
