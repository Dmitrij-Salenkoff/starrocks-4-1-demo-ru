-- Посмотрите чеки за оба дня.
SELECT receipt_id, sale_day, coffee, cups
FROM cafe_sales
ORDER BY sale_day, receipt_id;

-- Сколько чашек продали 3 января?
SELECT SUM(cups) AS cups
FROM cafe_sales
WHERE sale_day = '2026-01-03';

-- Сколько было чеков и видов кофе в этот день?
SELECT SUM(cups) AS cups, COUNT(*) AS receipts, COUNT(DISTINCT coffee) AS coffee_types
FROM cafe_sales
WHERE sale_day = '2026-01-03';

-- Как распределились чашки по напиткам?
SELECT coffee, SUM(cups) AS cups
FROM cafe_sales
WHERE sale_day = '2026-01-03'
GROUP BY coffee
ORDER BY coffee;

-- Сколько было продано вчера и за весь период?
SELECT SUM(cups) AS yesterday_cups
FROM cafe_sales
WHERE sale_day = '2026-01-02';

SELECT SUM(cups) AS all_cups
FROM cafe_sales;
