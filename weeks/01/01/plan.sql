-- Как StarRocks планирует посчитать чашки?
EXPLAIN
SELECT SUM(cups) AS cups
FROM cafe_sales
WHERE sale_day = '2026-01-03';

-- Получите сам ответ.
SELECT SUM(cups) AS cups
FROM cafe_sales
WHERE sale_day = '2026-01-03';

-- Выполните запрос ещё раз и откройте его профиль.
EXPLAIN ANALYZE
SELECT SUM(cups) AS cups
FROM cafe_sales
WHERE sale_day = '2026-01-03';
