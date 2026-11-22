"""Grade a learner's point-in-time query against generated payment histories."""
import argparse
import random
import sys
import uuid
from collections import Counter
from pathlib import Path

import sqlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COLUMNS = ("cut", "provider", "event_key", "merchant", "currency", "kind", "signed_minor")
CUTS = [("first", 100), ("revised", 200), ("final", 300)]


def fixture(seed):
    """Construct labelled cases directly from their stories."""
    rng = random.Random(seed)
    events = []
    labels = []
    providers = ["p" + str(x) for x in rng.sample(range(10, 99), 2)]
    a, b = providers
    keys = ["e" + str(x) for x in rng.sample(range(100, 999), 6)]
    capture, chargeback, disputed, moved, declined, late = keys
    amount, correction, fee = rng.sample(range(120, 950), 3)
    merchant, other = rng.sample(range(1, 21), 2)

    def delivery(provider, key, rev, arrived, day, owner, cur, kind, cents):
        events.append((provider, key, rev, arrived, day, owner, cur, kind, cents))

    def book(cut_names, provider, key, owner, cur, kind, signed):
        labels.extend((cut, provider, key, owner, cur, kind, signed) for cut in cut_names)

    first, revised, final = (cut for cut, _ in CUTS)
    # Equal identifiers at two providers denote separate movements. The first
    # provider's higher revision arrives exactly at the first exclusive cutoff.
    delivery(a, capture, 1, 20, 1, merchant, "USD", "capture", amount)
    delivery(a, capture, 1, 30, 1, merchant, "USD", "capture", amount)
    delivery(a, capture, 2, 100, 1, merchant, "USD", "capture", correction)
    delivery(a, capture, 1, 185, 1, merchant, "USD", "capture", amount)
    delivery(b, capture, 1, 21, 1, other, "EUR", "capture", amount)
    book([first], a, capture, merchant, "USD", "capture", amount)
    book([revised, final], a, capture, merchant, "USD", "capture", correction)
    book([first, revised, final], b, capture, other, "EUR", "capture", amount)

    delivery(a, chargeback, 1, 45, 1, merchant, "USD", "refund", fee)
    book([first, revised, final], a, chargeback, merchant, "USD", "refund", -fee)

    # A merchant-only conflict is invisible to checks comparing just amounts.
    delivery(b, disputed, 1, 40, 1, other, "USD", "capture", fee)
    delivery(b, disputed, 2, 141, 1, other, "USD", "capture", correction)
    delivery(b, disputed, 2, 142, 1, merchant, "USD", "capture", correction)
    delivery(b, disputed, 3, 250, 1, merchant, "USD", "capture", correction)
    book([first], b, disputed, other, "USD", "capture", fee)
    book([final], b, disputed, merchant, "USD", "capture", correction)

    delivery(a, moved, 1, 75, 1, other, "EUR", "capture", amount)
    delivery(a, moved, 2, 150, 2, other, "EUR", "capture", amount)
    book([first], a, moved, other, "EUR", "capture", amount)
    delivery(a, declined, 1, 65, 1, merchant, "USD", "failed", amount)
    delivery(b, late, 1, 200, 1, other, "EUR", "refund", fee)
    book([final], b, late, other, "EUR", "refund", -fee)
    rng.shuffle(events)
    return events, Counter(labels)


def compare(cursor, query, seed, expected):
    cursor.execute(query)
    names = tuple(field[0].lower() for field in cursor.description or ())
    if names != COLUMNS:
        raise ValueError(f"Expected columns {COLUMNS}, received {names}")
    actual = Counter(tuple(row) for row in cursor.fetchall())
    missing, extra = expected - actual, actual - expected
    if missing or extra:
        print(f"mismatch seed {seed} | missing={sum(missing.values())} extra={sum(extra.values())}")
        for label, differences in [("missing", missing), ("extra", extra)]:
            for row, copies in list(differences.items())[:5]:
                print(f"  {label} x{copies}: {row}")
        return False
    print(f"PASS seed {seed}: {sum(expected.values())} keyed rows, three cutoffs")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", type=Path, required=True, help="One SELECT or WITH query, relative to your current directory")
    parser.add_argument("--seed", action="append", type=int, help="Repeat for additional histories")
    args = parser.parse_args()
    pieces = sqlparse.split(args.query.read_text(encoding="utf-8"))
    if len(pieces) != 1 or sqlparse.parse(pieces[0])[0].get_type() != "SELECT":
        parser.error("The answer must be one SELECT statement, optionally starting with WITH.")
    sys.path.insert(0, str(ROOT))
    from lab import connect, verify_owner
    verify_owner(HERE)
    database = "sr41_assessment_" + uuid.uuid4().hex[:12]
    passed = True
    with connect() as conn, conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE {database}")
        try:
            cursor.execute(f"USE {database}")
            cursor.execute("""CREATE TABLE assessment_cutoffs (cut VARCHAR(12), cutoff_tick INT)
                DUPLICATE KEY(cut) DISTRIBUTED BY HASH(cut) BUCKETS 1
                PROPERTIES ("replication_num"="1")""")
            cursor.executemany("INSERT INTO assessment_cutoffs VALUES (%s,%s)", CUTS)
            cursor.execute("""CREATE TABLE assessment_input (
                provider VARCHAR(10), event_key VARCHAR(12), rev INT, received_tick INT, event_day INT,
                merchant INT, currency CHAR(3), kind VARCHAR(12), amount_minor BIGINT)
                DUPLICATE KEY(provider,event_key) DISTRIBUTED BY HASH(event_key) BUCKETS 1
                PROPERTIES ("replication_num"="1")""")
            for seed in args.seed or [11, 29, 47]:
                events, expected = fixture(seed)
                cursor.execute("TRUNCATE TABLE assessment_input")
                cursor.executemany("INSERT INTO assessment_input VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", events)
                if not compare(cursor, pieces[0], seed, expected):
                    passed = False
        finally:
            cursor.execute(f"DROP DATABASE {database}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
