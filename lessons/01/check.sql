SELECT CASE WHEN COUNT(*) = 3
         AND SUM(CASE WHEN event_day = '2026-01-12' AND capture_count = 2
                       AND gross_minor = 20000 AND refund_minor = 2000
                       AND net_minor = 18000 THEN 1 ELSE 0 END) = 1
         AND SUM(CASE WHEN event_day = '2026-01-13' AND capture_count = 1
                       AND gross_minor = 6000 AND refund_minor = 8000
                       AND net_minor = -2000 THEN 1 ELSE 0 END) = 1
         AND SUM(CASE WHEN event_day = '2026-01-14' AND capture_count = 0
                       AND gross_minor = 0 AND refund_minor = 0
                       AND net_minor = 0 THEN 1 ELSE 0 END) = 1
       THEN 1 ELSE 0 END AS passed
FROM sr01.daily_revenue;
