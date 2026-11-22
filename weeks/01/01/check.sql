SELECT IF(a.n=131072 AND b.n=131072 AND a.ids=131072 AND b.ids=131072
          AND a.total=78544256 AND b.total=78544256 AND m.same_rows=131072,1,0) AS ok
FROM (SELECT COUNT(*) n,COUNT(DISTINCT event_id) ids,SUM(cents) total FROM sr_date_tenant) a
CROSS JOIN (SELECT COUNT(*) n,COUNT(DISTINCT event_id) ids,SUM(cents) total FROM sr_event_hash) b
CROSS JOIN (SELECT COUNT(*) same_rows FROM sr_date_tenant a JOIN sr_event_hash b
    ON a.event_id=b.event_id AND a.tenant_id=b.tenant_id AND a.event_day=b.event_day AND a.cents=b.cents) m;
