#!/usr/bin/env python3
"""Assemble Harbor v0.25.x task packages from specs/ into tasks/.

Each spec in specs/<name>/ provides solution.patch + test_feature.py.
This script writes, per task:
  tasks/<name>/task.toml            (incl. repository + base_commit)
  tasks/<name>/instruction.md       (only file the evaluated AI sees)
  tasks/<name>/environment/Dockerfile
  tasks/<name>/solution/solve.sh + solution.patch
  tasks/<name>/tests/{Dockerfile,test.sh,run_verification.py,
                      test_feature.py,fail_to_pass.json,pass_to_pass.json}
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_COMMIT = "08b803cf32ceb2ae6a772c62d5da42757a897d44"
REPO_URL = "https://github.com/pallets/click"
BASE_WORKTREE = ROOT / "click-base-wt"

TASKS = {
    "duration-type": {
        "title": "Add a Duration parameter type to Click",
        "description": "Implement click.Duration, a parameter type that parses human-readable duration strings such as '1h30m' into datetime.timedelta values.",
    },
    "mutex-options": {
        "title": "Add mutually exclusive option groups to Click",
        "description": "Add an exclusive_group parameter to click.Option so that providing two options of the same group is a usage error.",
    },
    "command-aliases": {
        "title": "Add subcommand aliases to Click groups",
        "description": "Allow commands to declare aliases so a subcommand can be invoked by alternate names, shown in its help.",
    },
    "group-default": {
        "title": "Add a default subcommand to Click groups",
        "description": "Add a default parameter to click.Group: with no arguments, or an unknown first argument, the default subcommand runs with the remaining arguments.",
    },
    "nushell-completion": {
        "title": "Add Nushell shell completion support to Click",
        "description": "Add a NushellComplete class so Click's shell completion works in Nushell like it does in bash, zsh, fish and PowerShell.",
    },
}

ENV_DOCKERFILE = f"""FROM python:3.12-slim

RUN apt-get update \\
    && apt-get install -y --no-install-recommends git \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone {REPO_URL}.git . \\
    && git checkout {BASE_COMMIT}

RUN pip install --no-cache-dir -e . pytest==8.4.1
"""

TESTS_DOCKERFILE = """FROM python:3.12-slim

RUN pip install --no-cache-dir pytest==8.4.1

WORKDIR /app

COPY . /tests/
"""

SOLVE_SH = """#!/bin/bash
# Apply the reference implementation patch to the repository at /app.
set -e
cd /app
PATCH=""
for candidate in "$(dirname "$0")/solution.patch" /solution/solution.patch ./solution.patch; do
    if [ -f "$candidate" ]; then PATCH="$candidate"; break; fi
done
if [ -z "$PATCH" ]; then echo "solution.patch not found" >&2; exit 1; fi
git apply "$PATCH"
echo "Reference solution applied from $PATCH"
"""

TEST_SH = """#!/bin/bash
# Reward = share of passing feature tests, or 0.0 if any existing
# (regression) test fails. Written to /logs/verifier/reward.txt.
mkdir -p /logs/verifier
python3 /tests/run_verification.py
"""

RUN_VERIFICATION = '''#!/usr/bin/env python3
"""Run feature tests + the full existing Click suite and compute reward.

reward = (feature tests passed / feature tests total) if every existing
test passes, else 0.0. This makes the "nop" agent score 0.0 (all feature
tests fail on the base commit) and the oracle score 1.0.
"""
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

ENV = dict(os.environ, PYTHONPATH="/app/src")


def run_suite(args, xml_path):
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         f"--junitxml={xml_path}", *args],
        cwd="/app", env=ENV, capture_output=True, text=True,
    )
    tree = ET.parse(xml_path)
    total = failures = errors = skipped = 0
    for suite in tree.getroot().iter("testsuite"):
        total += int(suite.get("tests", 0))
        failures += int(suite.get("failures", 0))
        errors += int(suite.get("errors", 0))
        skipped += int(suite.get("skipped", 0))
    return total, failures + errors, skipped


def main():
    reg_total, reg_bad, _ = run_suite(["tests"], "/tmp/regression.xml")
    feat_total, feat_bad, feat_skip = run_suite(
        ["/tests/test_feature.py"], "/tmp/feature.xml"
    )
    feat_passed = feat_total - feat_bad - feat_skip
    fraction = (feat_passed / feat_total) if feat_total else 0.0
    reward = fraction if reg_bad == 0 else 0.0
    print(f"regression: {reg_total - reg_bad}/{reg_total} passed")
    print(f"feature: {feat_passed}/{feat_total} passed")
    print(f"reward: {reward}")
    with open("/logs/verifier/reward.txt", "w") as fh:
        fh.write(str(reward))
    summary = {
        "reward": reward,
        "regression_total": reg_total,
        "regression_failed": reg_bad,
        "feature_total": feat_total,
        "feature_passed": feat_passed,
    }
    with open("/logs/verifier/rewards.json", "w") as fh:
        json.dump(summary, fh, indent=2)


if __name__ == "__main__":
    main()
'''


def collect_ids(pytest_args, cwd, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", *pytest_args],
        cwd=cwd, env=env, capture_output=True, text=True,
    )
    ids = [ln.strip() for ln in out.stdout.splitlines() if "::" in ln]
    return ids


def main():
    python = str(ROOT / ".venv" / "bin" / "python")
    # pass_to_pass: every existing test at the base commit.
    pass_to_pass = collect_ids(
        ["tests"], cwd=BASE_WORKTREE,
        env_extra={"PYTHONPATH": str(BASE_WORKTREE / "src")},
    )
    # pytest binary from the venv but with this interpreter for collection.
    print(f"pass_to_pass: {len(pass_to_pass)} tests")

    for name, meta in TASKS.items():
        spec = ROOT / "specs" / name
        pkg = ROOT / "tasks" / name
        if pkg.exists():
            shutil.rmtree(pkg)
        (pkg / "environment").mkdir(parents=True)
        (pkg / "solution").mkdir()
        (pkg / "tests").mkdir()

        fail_to_pass = collect_ids(
            [str(spec / "test_feature.py")], cwd=ROOT,
            env_extra={"PYTHONPATH": str(BASE_WORKTREE / "src")},
        )
        # Node ids come out as paths relative to cwd; normalize to file::name.
        fail_to_pass = [
            "test_feature.py::" + node.split("::", 1)[1] for node in fail_to_pass
        ]
        print(f"{name}: fail_to_pass {len(fail_to_pass)}")

        (pkg / "task.toml").write_text(f"""schema_version = "1.4"

[metadata]
name = "{name}"
description = "{meta['description']}"
authors = ["Abhishek Phukan <noble02487@gmail.com>"]
repository = "{REPO_URL}"
base_commit = "{BASE_COMMIT}"
license = "BSD-3-Clause"

[verifier]
timeout_sec = 900.0
environment_mode = "separate"

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 600.0
""")
        shutil.copy(spec / "instruction.md", pkg / "instruction.md")
        (pkg / "environment" / "Dockerfile").write_text(ENV_DOCKERFILE)
        (pkg / "solution" / "solve.sh").write_text(SOLVE_SH)
        shutil.copy(spec / "solution.patch", pkg / "solution" / "solution.patch")
        (pkg / "tests" / "Dockerfile").write_text(TESTS_DOCKERFILE)
        (pkg / "tests" / "test.sh").write_text(TEST_SH)
        (pkg / "tests" / "run_verification.py").write_text(RUN_VERIFICATION)
        shutil.copy(spec / "test_feature.py", pkg / "tests" / "test_feature.py")
        (pkg / "tests" / "fail_to_pass.json").write_text(
            json.dumps(fail_to_pass, indent=2)
        )
        (pkg / "tests" / "pass_to_pass.json").write_text(
            json.dumps(pass_to_pass, indent=2)
        )
        print(f"built tasks/{name}")


if __name__ == "__main__":
    main()
