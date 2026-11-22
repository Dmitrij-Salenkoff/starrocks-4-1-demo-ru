"""Compare the revised January 1 report to a separate statement, then inject two offsetting errors."""
from collections import Counter
from dataclasses import dataclass, replace
from os import environ

import pymysql


@dataclass(frozen=True)
class Posting:
    merchant_id: int
    currency: str
    entry_kind: str
    signed_minor: int


def indexed(rows):
    result = {}
    for event_key, merchant, currency, kind, amount in rows:
        if event_key in result:
            raise ValueError(f"Duplicate business key in reconciliation input: {event_key}")
        result[event_key] = Posting(merchant, currency, kind, amount)
    return result


def currency_totals(entries):
    by_currency = Counter()
    for entry in entries.values():
        by_currency[entry.currency] += entry.signed_minor
    return dict(by_currency)


def differences(internal, statement):
    return {
        key: (internal.get(key), statement.get(key))
        for key in sorted(set(internal) | set(statement))
        if internal.get(key) != statement.get(key)
    }


def describe(name, internal, statement):
    totals = currency_totals(internal)
    reference = currency_totals(statement)
    gaps = differences(internal, statement)
    for currency in sorted(set(totals) | set(reference)):
        amount = totals.get(currency, 0)
        expected = reference.get(currency, 0)
        print(f"{name} {currency}: internal={amount} statement={expected} residual={amount-expected}")
    for key, (actual, expected) in gaps.items():
        print(f"  {key}: {actual} | {expected}")
    return gaps


def experiment(internal, statement):
    baseline = describe("baseline", internal, statement)
    baseline_totals = currency_totals(internal)
    if baseline_totals != {"USD": 2300, "EUR": 500} or currency_totals(statement) != {"USD": 2550, "EUR": 500}:
        raise ValueError("Unexpected fixture totals. Restore the lesson with lab.py setup 01/01.")
    if baseline != {"Q": (None, Posting(8, "USD", "capture", 250))}:
        raise ValueError(f"Unexpected reconciliation baseline: {baseline}")

    changed = internal.copy()
    changed["A"] = replace(changed["A"], signed_minor=changed["A"].signed_minor+100)
    changed["B"] = replace(changed["B"], signed_minor=changed["B"].signed_minor-100)
    after = describe("injected", changed, statement)
    if currency_totals(changed) != baseline_totals or set(after) != {"A", "B", "Q"}:
        raise AssertionError("The total and the set of detected keys do not satisfy the experiment")
    print("PASS: totals unchanged; reconciliation detected A, B, Q")


def main():
    columns = "event_key,merchant_id,currency,entry_kind,signed_minor"
    with pymysql.connect(
        host=environ.get("SR_HOST", "127.0.0.1"), port=int(environ.get("SR_PORT", "9030")),
        user=environ.get("SR_USER", "root"), password=environ.get("SR_PASSWORD", ""), database="course",
    ) as conn, conn.cursor() as cur:
        cur.execute(f"SELECT {columns} FROM case_v_postings WHERE checkpoint='revised'")
        internal = indexed(cur.fetchall())
        cur.execute(f"SELECT {columns} FROM case_statement WHERE checkpoint='revised'")
        statement = indexed(cur.fetchall())
    experiment(internal, statement)


if __name__ == "__main__":
    main()
