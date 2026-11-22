"""Run one isolated StarRocks lab from its numbered lesson directory."""
import argparse
import subprocess
import sys
from pathlib import Path

import pymysql
import sqlparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["setup", "solve", "check", "reset"])
    args = parser.parse_args()
    folder = Path.cwd()
    if folder.parent != Path(__file__).resolve().parents[1] / "lessons" or not folder.name.isdigit():
        parser.error("Run inside lessons/NN in this repository")
    database = f"sr{folder.name}"
    # One connection per script preserves SET, USE and session-scoped query profiles.
    with pymysql.connect(host="127.0.0.1", port=9030, user="root", password="",
                         database=None if args.action in {"setup","reset"} else database,
                         autocommit=True, charset="utf8mb4", connect_timeout=10, read_timeout=600) as conn:
        with conn.cursor() as cur:
            if args.action == "reset":
                cur.execute(f"DROP DATABASE IF EXISTS `{database}`")
                print("Removed local lab database", database)
                return 0
            if args.action == "solve":
                hook = folder / "before_solve.py"
                if hook.is_file():
                    subprocess.run([sys.executable, str(hook)], cwd=folder, check=True)
            path = folder / {"setup":"setup.sql","solve":"solution.sql","check":"check.sql"}[args.action]
            result = None
            for idx, statement in enumerate(sqlparse.split(path.read_text(encoding="utf-8")), start=1):
                try:
                    cur.execute(statement)
                except pymysql.MySQLError:
                    print(f"{path.name}, statement {idx}: {statement[:220]}", file=sys.stderr)
                    raise
                if cur.description:
                    result = cur.fetchall()
                    print(" | ".join(col[0] for col in cur.description))
                    for row in result[:120]:
                        print(" | ".join(str(val) for val in row))
            if args.action == "check":
                passed = result is not None and len(result) == 1 and len(result[0]) == 1 and str(result[0][0]) == "1"
                print("PASS" if passed else "FAIL")
                return 0 if passed else 1
    hook = folder / "after_solve.py"
    if args.action == "solve" and hook.is_file():
        subprocess.run([sys.executable, str(hook)], cwd=folder, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
