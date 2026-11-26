# Technical Documentation — Coding Task Factory

## Strategy (one reusable generation method, five tasks)

Every task in this submission is produced by the same five-step factory strategy,
implemented in `factory/build_package.py`:

1. **Pin a green baseline.** Clone the starter repository and choose a real commit
   where the *entire* existing test suite passes (Click @
   `08b803cf32ceb2ae6a772c62d5da42757a897d44`: 2,653 collected tests, 0 failures).
   The full 40-character hash is recorded in every `task.toml` as `base_commit`.
2. **Pick a feature that does not exist upstream**, in a distinct subsystem, and
   specify it completely in `instruction.md` (API, behavior, edge cases, error
   semantics) — the only file the evaluated AI ever sees.
3. **Write the feature tests first** (`test_feature.py`). Every test must fail on
   the base commit for the right reason (feature absent), which is verified, not
   assumed. These tests become the package's `fail_to_pass.json` set.
4. **Implement the reference solution** on a branch, keeping the change minimal
   and idiomatic to the codebase. Export it as `solution/solution.patch`;
   `solution/solve.sh` applies it with `git apply`.
5. **Verify both directions.** nop (base + tests) must score reward **0.0**;
   oracle (base + patch + tests) must score **1.0** with the full existing suite
   still green. The verifier (`tests/run_verification.py`) computes
   `reward = feature_tests_passed / feature_tests_total`, forced to `0.0` if any
   regression test fails, matching the brief's reward definition.

## Task-variation strategy (why the five tasks are substantively different)

Variation is by **subsystem and mechanism**, not rewording:

- `duration-type` — a new *parameter type* (string → `timedelta` parsing grammar).
- `mutex-options` — new *cross-option validation* at invoke time, driven by
  parameter-source tracking (command line / env var count, defaults don't).
- `command-aliases` — new *name resolution* in group dispatch plus help rendering.
- `group-default` — new *fallback routing* in group dispatch (no-args and
  unknown-first-arg paths, `no_args_is_help` interplay, chain mode excluded).
- `nushell-completion` — a new *shell backend* in the completion subsystem
  (source script generation + completion-arg protocol + output framing).

Each task touches different files (`types.py`, `core.py` validation,
`core.py` dispatch ×2 by different mechanisms, `shell_completion.py`), demands a
different kind of reasoning from the evaluated model, and has its own
independently written test suite (25 / 10 / 9 / 6 / 5 feature tests).

## Design decisions

- **Reward integrity first.** The regression gate is the *entire* existing suite
  (2,653 tests, listed in `pass_to_pass.json`), not a hand-picked subset — a
  solution that breaks anything scores 0.
- **No network at verify time.** The verifier imports Click via
  `PYTHONPATH=/app/src` and needs only pytest; package installation happens at
  environment build time.
- **Features are real upstream gaps.** Each candidate was checked against the
  base tree (e.g. Click has `DateTime` but no duration type; arguments already
  support `envvar`, so that early candidate was discarded; PowerShell completion
  exists, Nushell does not).
- **Error semantics follow Click conventions** — `ParamType.fail` for bad values,
  `UsageError` (exit code 2) for conflicting options — so tasks test whether a
  model can match a codebase's idioms, not just produce code.

## Assumptions

- Judges run Harbor v0.25.x with Docker; task environments build from
  `python:3.12-slim` and clone Click from GitHub at build time.
- The evaluated agent works in `/app` (the repo checkout at `base_commit`).

## Tools and models used (declared per the participant guide)

- The task packages, reference implementations, tests, factory code and this
  documentation were produced with the help of an AI coding assistant
  (Muse, by Meta), directed and reviewed by the participant.
- No external datasets were used. The only third-party code is the starter
  repository itself (pallets/click, BSD-3-Clause), cloned unmodified at the
  pinned commit inside each task environment.

## Reused components

- Harbor v0.25.x task scaffolding conventions (task.toml schema 1.4, separate
  verifier environment, `solve.sh` oracle convention).
- SWE-bench-style `fail_to_pass.json` / `pass_to_pass.json` test manifests.
