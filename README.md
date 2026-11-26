# Coding Task Factory — Innodata AI Hackathon 2026 (Track 1)

**Participant:** Abhishek Phukan (solo) · **Track:** Coding Task Factory · **Framework:** Harbor v0.25.x

A reusable pipeline that turns a real open-source codebase into **solvable, testable
feature-development tasks** for evaluating AI coding systems. Each generated task package
contains clear requirements (`instruction.md`), a reference implementation
(`solution/solution.patch`), feature tests plus the full existing regression suite as the
pass-to-pass set, and a verifier whose reward is the share of passing feature tests —
**0.0 if any existing test breaks**.

## Chosen repository

- **pallets/click** (Python, pytest) — https://github.com/pallets/click
- Base commit: `08b803cf32ceb2ae6a772c62d5da42757a897d44` (verified: all 2,653 collected
  existing tests pass at this commit)

## The five generated tasks

| Task | Area | Feature (verified absent upstream) |
|---|---|---|
| `duration-type` | Parameter types | `click.Duration` — parses `"1h30m"`, `"2d"`, `"500ms"` into `timedelta` |
| `mutex-options` | Core validation | `Option(exclusive_group=...)` — usage error when two group members are given |
| `command-aliases` | Group dispatch | `@group.command(aliases=[...])` — alternate subcommand names |
| `group-default` | Group dispatch | `Group(default="run")` — fallback subcommand for no/unknown first arg |
| `nushell-completion` | Shell completion | `NushellComplete` — Nushell support next to bash/zsh/fish/PowerShell |

## Layout

- `factory/build_package.py` — the generator: assembles one Harbor package per spec
- `specs/<task>/` — per-task source of truth: `instruction.md`, `test_feature.py`, `solution.patch`
- `tasks/<task>/` — generated Harbor packages (task.toml, environment/, solution/, tests/)
- `TECHNICAL.md` — design decisions, variation strategy, assumptions, tool declaration
- `VALIDATION.md` — nop/oracle validation evidence for every task

## Regenerate the packages

```bash
python3 -m venv .venv && .venv/bin/pip install "harbor==0.25.*"
.venv/bin/python factory/build_package.py
.venv/bin/harbor lint tasks/*
```

## Validate a task (Harbor, Docker)

```bash
harbor run -p tasks/duration-type -a nop    -k 1 -o out-nop    --no-delete -y   # reward 0.0
harbor run -p tasks/duration-type -a oracle -k 1 -o out-oracle --no-delete -y   # reward 1.0
```

The same nop/oracle checks were also run without Docker (plain pytest, two clean
checkouts) — see `VALIDATION.md` for the recorded results.
