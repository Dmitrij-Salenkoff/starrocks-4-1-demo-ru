SELECT IF(d.n=7 AND d.events=6 AND d.raw_minor=4500 AND d.gross_minor=3300
      AND p.closed_rows=5 AND p.revised_rows=4 AND p.usd_closed=2300 AND p.usd_revised=2300
      AND p.eur_closed=500 AND p.eur_revised=500 AND p.refund_closed=-300 AND p.refund_revised=-300
      AND q.n=2 AND q.quarantined_q=2 AND q.low_q=250 AND q.high_q=260
      AND g.n=1 AND g.expected_gap=1,1,0) AS ok
FROM (
    SELECT COUNT(*) AS n,COUNT(DISTINCT event_id) AS events,
           SUM(CASE WHEN is_capture THEN amount_minor ELSE 0 END) AS raw_minor,
           SUM(CASE WHEN is_capture AND rn=1 THEN amount_minor ELSE 0 END) AS gross_minor
    FROM (SELECT event_id,amount_minor,event_kind='captured' AND currency='USD' AS is_capture,
                 ROW_NUMBER() OVER(PARTITION BY event_id ORDER BY delivery_id DESC) AS rn
          FROM demo_deliveries) ranked
) d
CROSS JOIN (
    SELECT SUM(IF(checkpoint='closed',1,0)) AS closed_rows,
           SUM(IF(checkpoint='revised',1,0)) AS revised_rows,
           SUM(IF(checkpoint='closed' AND currency='USD',signed_minor,0)) AS usd_closed,
           SUM(IF(checkpoint='revised' AND currency='USD',signed_minor,0)) AS usd_revised,
           SUM(IF(checkpoint='closed' AND currency='EUR',signed_minor,0)) AS eur_closed,
           SUM(IF(checkpoint='revised' AND currency='EUR',signed_minor,0)) AS eur_revised,
           SUM(IF(checkpoint='closed' AND entry_kind='refund',signed_minor,0)) AS refund_closed,
           SUM(IF(checkpoint='revised' AND entry_kind='refund',signed_minor,0)) AS refund_revised
    FROM case_v_postings
) p
CROSS JOIN (
    SELECT COUNT(*) AS n,SUM(IF(checkpoint='revised' AND event_key='Q' AND src_version=2,1,0)) AS quarantined_q,
           MIN(amount_minor) AS low_q,MAX(amount_minor) AS high_q
    FROM case_v_classified WHERE variants>1
) q
CROSS JOIN (
    SELECT COUNT(*) AS n,SUM(IF(checkpoint='revised' AND event_key='Q' AND reason='missing_internal'
                    AND internal_minor IS NULL AND statement_minor=250,1,0)) AS expected_gap
    FROM case_v_gaps
) g;
