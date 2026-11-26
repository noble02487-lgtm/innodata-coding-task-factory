# Validation Evidence

Baseline: pallets/click @ `08b803cf32ceb2ae6a772c62d5da42757a897d44`
Full existing suite at baseline: **2,653 collected tests — all pass**
(2,628 passed, 24 skipped, 1 xfailed when run; 0 failures).

Method: for every generated package, the package's own verifier
(`tests/run_verification.py`) was executed against two clean checkouts —
the untouched base commit (nop) and the base commit with
`solution/solution.patch` applied (oracle). Reward rule: share of passing
feature tests, forced to 0.0 if any regression test fails.

| Task | Feature tests | nop reward | oracle reward | Regression (oracle) |
|---|---|---|---|---|
| duration-type | 25 | **0.0** (0/25) | **1.0** (25/25) | 2653/2653 pass |
| mutex-options | 10 | **0.0** (0/10) | **1.0** (10/10) | full suite pass |
| command-aliases | 9 | **0.0** (0/9) | **1.0** (9/9) | full suite pass |
| group-default | 6 | **0.0** (0/6) | **1.0** (6/6) | full suite pass |
| nushell-completion | 5 | **0.0** (0/5) | **1.0** (5/5) | full suite pass |

Static check: `harbor lint` (Harbor 0.25.0) reports **no findings** for all
five packages (after pinning `pytest==8.4.1` and declaring
`verifier.environment_mode = "separate"`).

Notable failure found and fixed during validation: the first
`group-default` build scored oracle < 1.0 because a group with a default
command still had `no_args_is_help` enabled, so invoking with no arguments
showed help instead of dispatching. The reference implementation now
defaults `no_args_is_help` off when a default command is set (an explicit
user setting is still respected), and the package re-validated at 1.0.

Docker note: the development VM used for authoring cannot run Docker
(no NET_ADMIN capability / overlayfs), so the recorded nop/oracle runs
above are the pytest-level equivalents executed with the packages' own
verifier script; the identical packages are Harbor-lint clean and ready
for `harbor run -a nop / -a oracle` in a Docker-capable environment.
