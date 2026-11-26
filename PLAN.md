# Innodata AI Hackathon 2026 — Track 1 Build Plan

- Event: Innodata AI Hackathon 2026 (Hack2skill), Track 1 — Coding Task Factory
- Participant: Abhishek Phukan (solo), registered 26 Nov 2026
- Submission deadline: 6 Dec 2026, 11:55 PM IST (dashboard form time)
- Prizes: 1st ₹5,00,000 · 2nd ₹3,00,000 · 3rd ₹2,00,000

## Chosen starter repo
- **pallets/click** (Python, pytest)
- Base commit: `08b803cf32ceb2ae6a772c62d5da42757a897d44`
- Verified 26 Nov: full suite from repo root = **2628 passed, 24 skipped, 1 xfailed, 0 failed**

## The factory (strategy)
`factory/build_package.py` assembles one Harbor v0.25.x package per task spec in `specs/`:
- `task.toml` — Harbor schema 1.4 + repo URL + full base_commit hash
- `instruction.md` — the only file the evaluated AI sees
- `environment/Dockerfile` — python:3.12-slim + git, clones click, checks out base_commit, `pip install -e .`
- `solution/solve.sh` + `solution/solution.patch` — reference implementation (git apply)
- `tests/test.sh` — reward = share of passing feature tests, but **0.0 if any regression test fails**
  (regression = click's full existing suite); writes float reward to /logs/verifier/reward.txt
- `tests/test_feature.py`, `tests/fail_to_pass.json`, `tests/pass_to_pass.json`, `tests/Dockerfile`
- Local validator (`factory/validate_local.py`) proves nop = 0.0 and oracle = 1.0 with plain
  pytest (two clean checkouts), because this VM cannot run Docker (no NET_ADMIN / overlayfs).
  Harbor Docker validation runs on the laptop (Docker present at /usr/bin/docker).

## The 5 tasks (all verified ABSENT upstream at base commit)
1. **duration-type** (types) — new `click.Duration` type: "1h30m", "2d", "45s", "1w2d", plain
   number = seconds → `datetime.timedelta`; bad input → BadParameter.
2. **mutually-exclusive-options** (core validation) — `Option(exclusive_group="name")`;
   UsageError when 2+ options of one group are explicitly provided.
3. **command-aliases** (core dispatch) — `@group.command(aliases=[...])`; aliases resolve,
   appear in help, canonical name stays primary.
4. **group-default-command** (core dispatch) — `Group(default="name")`: when the first arg is
   not a known subcommand (or no arg), remaining args go to the default command.
5. **nushell-completion** (shell completion) — `NushellComplete` class + registration so
   `_CLICK_COMPLETE=nushell_complete` style activation works like bash/zsh/fish/powershell.

## Submission package (dashboard form)
- Challenges: Coding Task Factory
- Prototype Brief (≤1024 chars), Technology Stack (≤1024 chars)
- GitHub **public** repo link (factory + generated packages + validation logs)
- Demo Video Link (to record)
- Solution deck PDF (≤5 MB, from their Google Slides template)

## Validation log
- 26 Nov ~15:31 IST — base commit suite green (2628 passed).
- 26 Nov ~16:05 IST — **Task 1 duration-type DONE**: feature tests 25/25 FAIL on base (nop = 0.0),
  25/25 PASS with patch + full suite 2628 passed (oracle = 1.0). Patch: specs/duration-type/solution.patch.
- 26 Nov ~16:35 IST — **Task 2 mutex-options DONE**: 10/10 fail on base, 10/10 pass + 2628 regression.
- 26 Nov ~16:45 IST — **Task 3 command-aliases DONE**: 9/9 fail on base, 9/9 pass + 2628 regression.
- 26 Nov ~16:55 IST — **Task 4 group-default DONE**: 6/6 fail on base, 6/6 pass + 2628 regression
  (fix: no_args_is_help defaults off when a default command is set).
- 26 Nov ~17:05 IST — **Task 5 nushell-completion DONE**: collection error on base (class absent),
  5/5 pass + 2628 regression.
- **All 5 task implementations complete.**
- 26 Nov ~17:20 IST — **All 5 Harbor packages built + verified end-to-end** with the packages' own
  verifier script: every task nop = 0.0 / oracle = 1.0 (regression 2653/2653 in the sim).
  `harbor lint` clean on all 5 (after pinning pytest==8.4.1 + verifier separate mode).
- Next: README/tech docs, GitHub repo, deck, video, submit.
