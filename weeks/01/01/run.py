"""Measure FE pruning and reconcile queries across two StarRocks layouts."""
import argparse
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from lab import connect

LAYOUTS = ("sr_date_tenant", "sr_event_hash")
CASES = [
    ("day-and-tenant", "event_day='2026-01-03' AND tenant_id=7", (256,154528), ((1,1),(1,16))),
    ("day-only", "event_day='2026-01-03'", (32768,19662976), ((1,4),(1,16))),
    ("event-only", "event_id=65543", (1,643), ((4,16),(1,1))),
]


def explain_text(cursor, prefix, sql):
    cursor.execute(f"{prefix} {sql}")
    return "\n".join(str(value) for row in cursor.fetchall() for value in row if value is not None)


def scan_counts(plan):
    result = []
    for label in (r"partitions?|partitionRatio", r"tablets?|tabletRatio"):
        match = re.search(rf"\b(?:{label})\s*[:=]\s*(\d+)\s*/\s*(\d+)", plan, re.I)
        if match is None:
            raise ValueError(f"Cannot locate {label} in the FE scan plan:\n{plan}")
        result.append((int(match[1]), int(match[2])))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", action="store_true", help="also print actual EXPLAIN ANALYZE output")
    args = parser.parse_args()
    with connect() as connection, connection.cursor() as cur:
        cur.execute("USE course")
        for table in LAYOUTS:
            cur.execute("SHOW TABLET FROM " + table)
            names = [field[0].lower() for field in cur.description]
            ids = {r[names.index("tabletid")] for r in cur.fetchall()}
            if len(ids) != 16:
                raise RuntimeError(f"{table}: expected 16 logical tablets, found {len(ids)}")
            print(f"inventory {table}: {len(ids)} logical tablets")
        for name, predicate, expected_answer, expected_plans in CASES:
            for table, expected_plan in zip(LAYOUTS, expected_plans, strict=True):
                sql = f"SELECT COUNT(*),SUM(cents) FROM {table} WHERE {predicate}"
                raw = explain_text(cur,"EXPLAIN",sql)
                parts, tablets = scan_counts(raw)
                cur.execute(sql)
                actual = tuple(map(int,cur.fetchone()))
                print(f"{name} {table}: partition ratio={parts[0]}/{parts[1]}, "
                      f"tablet ratio={tablets[0]}/{tablets[1]}, selected={tablets[0]}/16 physical inventory, "
                      f"rows/cents={actual}")
                if (parts[0],tablets[0]) != expected_plan or actual != expected_answer:
                    raise AssertionError(f"Expected {expected_plan} and {expected_answer}\n{raw}")
                if args.profile and name == "day-and-tenant":
                    metrics = explain_text(cur,"EXPLAIN ANALYZE",sql)
                    print(f"\n--- actual profile: {table} ---\n{metrics}\n")
        print("PASS: data matches and pruning reverses on event_id")


if __name__ == "__main__":
    main()
