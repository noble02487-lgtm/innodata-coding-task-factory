#!/bin/bash
# Reward = share of passing feature tests, or 0.0 if any existing
# (regression) test fails. Written to /logs/verifier/reward.txt.
mkdir -p /logs/verifier
python3 /tests/run_verification.py
