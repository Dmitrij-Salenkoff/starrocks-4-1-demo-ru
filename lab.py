"""Start and inspect the disposable StarRocks classroom labs."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import pymysql
import sqlparse

ROOT = Path(__file__).resolve().parent
SQL_PORT = 9030


def compose(folder: Path, *args: str, capture: bool = False):
    return subprocess.run(
        ["docker", "compose", "-f", str(folder / "compose.yaml"), *args],
        cwd=folder, check=True, text=True, capture_output=capture,
    )


def verify_owner(folder: Path) -> None:
    # All stands expose the same host port. Stop a stale console from seeding a different lab.
    mapping = compose(folder, "port", "starrocks", str(SQL_PORT), capture=True).stdout.strip()
    if mapping != f"127.0.0.1:{SQL_PORT}":
        raise RuntimeError(f"The selected lab is not listening on 127.0.0.1:{SQL_PORT}: {mapping}")


def connect():
    return pymysql.connect(
        host="127.0.0.1", port=SQL_PORT, user="root", password="", charset="utf8mb4",
        autocommit=True, connect_timeout=4, read_timeout=600, write_timeout=60,
    )


def ready() -> None:
    deadline = time.monotonic() + 240
    last = "no live backend"
    while time.monotonic() < deadline:
        try:
            with connect() as conn, conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SHOW BACKENDS")
                if any(str(r["Alive"]).lower() in {"true", "1"} for r in cur.fetchall()):
                    cur.execute("CREATE DATABASE IF NOT EXISTS course")
                    # A BE can report Alive before its disk report allows tablet placement.
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS course.sr41_readiness (id INT NOT NULL)
                        DUPLICATE KEY(id) DISTRIBUTED BY HASH(id) BUCKETS 1
                        PROPERTIES ("replication_num"="1")
                    """)
                    cur.execute("SELECT COUNT(*) FROM course.sr41_readiness")
                    cur.fetchone()
                    cur.execute("DROP TABLE course.sr41_readiness")
                    return
        except pymysql.MySQLError as exc:
            last = str(exc)
        time.sleep(3)
    raise RuntimeError(f"StarRocks readiness timed out: {last}")


def execute(folder: Path, stage: str) -> None:
    path = folder / f"{stage}.sql"
    statements = sqlparse.split(path.read_text(encoding="utf-8"))
    if stage == "check" and len(statements) != 1:
        raise ValueError(f"{path} must contain exactly one result-producing statement")
    with connect() as conn, conn.cursor() as cur:
        cur.execute("USE course")
        for i, statement in enumerate(statements, 1):
            try:
                cur.execute(statement)
            except pymysql.MySQLError:
                print(f"{path.relative_to(ROOT)} [{i}]\n{statement}", file=sys.stderr)
                raise
            if cur.description:
                print(" | ".join(str(d[0]) for d in cur.description))
                rows = cur.fetchmany(41)
                for row in rows[:40]:
                    print(" | ".join("NULL" if v is None else str(v) for v in row))
                if len(rows) > 40:
                    print("…")
            if stage == "check":
                if not cur.description or len(rows) != 1 or len(rows[0]) != 1 or str(rows[0][0]) != "1":
                    raise RuntimeError("FAIL: the lab contract returned a value other than 1")
                print("PASS")


def main() -> None:
    labs = sorted(p.parent for p in (ROOT / "weeks").glob("*/*/compose.yaml"))
    lessons = {p.relative_to(ROOT / "weeks").as_posix(): p for p in labs}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "up", "status", "logs", "setup", "run", "explore", "check", "down"])
    parser.add_argument("lesson", nargs="?", choices=lessons)
    args = parser.parse_args()
    if args.action == "list":
        for key, path in lessons.items():
            title = (path / "README.md").read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
            print(f"{key}  {title}")
        return
    if not args.lesson:
        parser.error("Supply the lesson ID, for example 01/01")
    folder = lessons[args.lesson]
    if args.action == "up":
        compose(folder, "up", "--detach", "--wait", "--wait-timeout", "480")
        verify_owner(folder)
        ready()
    elif args.action == "down":
        compose(folder, "down", "--volumes", "--remove-orphans")
    elif args.action == "status":
        compose(folder, "ps", "--all")
    elif args.action == "logs":
        compose(folder, "logs", "--tail", "100")
    else:
        verify_owner(folder)
        if args.action == "run":
            driver = folder / "run.py"
            if not driver.is_file():
                parser.error("This lesson uses SQL only or a named experiment. Follow its README.")
            subprocess.run([sys.executable, str(driver)], cwd=ROOT, check=True)
        else:
            execute(folder, args.action)


if __name__ == "__main__":
    main()
