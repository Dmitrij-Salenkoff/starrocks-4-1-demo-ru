-- Starting hypothesis: every visible delivery is a booked movement.
-- Keep the output column names and implement the contract in the lesson.
SELECT c.cut, e.provider, e.event_key, e.merchant, e.currency, e.kind,
       CASE WHEN e.kind='refund' THEN -e.amount_minor ELSE e.amount_minor END AS signed_minor
FROM assessment_cutoffs AS c
JOIN assessment_input AS e ON e.received_tick < c.cutoff_tick
WHERE e.event_day=1 AND e.kind IN ('capture','refund');
