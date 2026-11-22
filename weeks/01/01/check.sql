SELECT IF(COUNT(*)=7 AND COUNT(DISTINCT event_id)=6 AND
          SUM(CASE WHEN is_capture AND rn=1 THEN amount_minor ELSE 0 END)=3300 AND
          SUM(CASE WHEN is_capture THEN amount_minor ELSE 0 END)=4500,1,0) AS ok
FROM (
    SELECT event_id, amount_minor, event_kind='captured' AND currency='USD' AS is_capture,
           ROW_NUMBER() OVER(PARTITION BY event_id ORDER BY delivery_id DESC) AS rn
    FROM demo_deliveries
) AS ranked;
