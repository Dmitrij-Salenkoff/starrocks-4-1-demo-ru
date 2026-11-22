"""Run one disposable lesson from setup through its acceptance checks."""
import argparse
import os
import shlex
import subprocess
import sys
import tomllib
import uuid

import sqlparse
from lab import ROOT, connect


def command(arguments, *, timeout=600, expect=0, contains=None):
    print("+", shlex.join(map(str, arguments)), flush=True)
    process = subprocess.run(
        arguments, cwd=ROOT, timeout=timeout, text=True, check=False,
        stdout=subprocess.PIPE if contains or expect else None,
        stderr=subprocess.STDOUT if contains or expect else None,
    )
    if process.stdout:
        print(process.stdout, end="" if process.stdout.endswith("\n") else "\n", flush=True)
    if process.returncode != expect:
        raise RuntimeError(f"Expected exit {expect}, got {process.returncode}")
    if contains and contains not in process.stdout:
        raise RuntimeError(f"Missing expected output: {contains!r}")


def check_experiment(folder, steps):
    for step in steps:
        if "python" in step:
            script, *args = step["python"]
            # Arguments denoting local CSV inputs are explicit paths from the repository root.
            command([sys.executable, folder / script, *args], expect=step.get("exit", 0),
                    contains=step.get("contains"))
            continue
        sql = (folder / step["file"]).read_text(encoding="utf-8") if "file" in step else step["sql"]
        with connect() as conn, conn.cursor() as cursor:
            cursor.execute("USE course")
            rows = None
            for statement in sqlparse.split(sql):
                print("+ SQL:", statement, flush=True)
                cursor.execute(statement)
                if cursor.description:
                    rows = [list(row) for row in cursor.fetchall()]
                    print(rows, flush=True)
            if "rows" in step and rows != step["rows"]:
                raise RuntimeError(f"Expected {step['rows']!r}, received {rows!r}")
            if "absent_first_column" in step:
                value = step["absent_first_column"]
                if rows is None or any(row[0] == value for row in rows):
                    raise RuntimeError(f"Expected a result set without {value!r} in its first column")


def main():
    folders = {path.parent.relative_to(ROOT / "weeks").as_posix(): path.parent
               for path in (ROOT / "weeks").glob("*/*/compose.yaml")}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", choices=sorted(folders))
    lesson = parser.parse_args().lesson
    folder = folders[lesson]
    recipe = folder / "smoke.toml"
    experiments = tomllib.loads(recipe.read_text(encoding="utf-8")) if recipe.is_file() else {}
    # An isolated project lets cleanup remove only containers and volumes created by this run.
    os.environ["COMPOSE_PROJECT_NAME"] = "sr41-smoke-" + uuid.uuid4().hex[:12]
    os.environ.update(SR_HOST="127.0.0.1", SR_PORT="9030", SR_USER="root", SR_PASSWORD="")

    def lab(action, timeout=600):
        command([sys.executable, ROOT / "lab.py", action, lesson], timeout=timeout)

    try:
        lab("up", timeout=1200)
        lab("setup")
        check_experiment(folder, experiments.get("before_run", []))
        if (folder / "run.py").is_file() and lesson.split("/")[0] in {"03", "04"}:
            lab("run")
        lab("explore")
        lab("check")
        check_experiment(folder, experiments.get("step", []))
    except BaseException:
        try:
            lab("logs", timeout=60)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            print(f"Could not retrieve container logs: {error}", file=sys.stderr)
        raise
    finally:
        lab("down", timeout=180)
    print(f"PASS {lesson}", flush=True)


if __name__ == "__main__":
    main()
