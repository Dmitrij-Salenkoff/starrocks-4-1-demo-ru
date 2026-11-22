SELECT SUM(cups) AS cups, COUNT(*) AS receipts, COUNT(DISTINCT coffee) AS coffee_types
FROM cafe_sales
WHERE sale_day = '2026-01-03';
