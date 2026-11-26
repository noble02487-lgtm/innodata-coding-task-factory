#!/usr/bin/env python3
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
