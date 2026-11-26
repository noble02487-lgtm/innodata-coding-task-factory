# Add mutually exclusive option groups to Click

The repository at `/app` is the Click command-line library (Python), checked out at a fixed commit. Implement a way to declare that certain options of a command must not be used together.

## Required API

- `click.Option` accepts a new keyword argument `exclusive_group` (a string naming a group, default `None`), stored as the attribute `option.exclusive_group`.

## Behavior

- When a command is invoked and **two or more options belonging to the same `exclusive_group` were explicitly provided**, invoking the command must fail with a usage error (exit code 2) whose message contains the words `mutually exclusive` and names the conflicting options (e.g. `--json` and `--yaml`).
- "Explicitly provided" means the value came from the command line or from an environment variable. Values that come from a default value or the default map do **not** count as provided — a command whose group members all have defaults must run normally, and providing only one member explicitly is fine.
- Providing zero or one member of a group is fine. Options in different groups do not interfere with each other. Options without an `exclusive_group` are unaffected.
- The check applies to options of plain commands as well as options declared on a group itself (checked when the group runs its callback dispatch).

## Example

```python
@click.command()
@click.option("--json", is_flag=True, exclusive_group="format")
@click.option("--yaml", is_flag=True, exclusive_group="format")
def cli(json, yaml):
    ...

# cli --json        -> runs
# cli --json --yaml -> Error: ... mutually exclusive ... (exit code 2)
```

All pre-existing tests in the repository's `tests/` directory must continue to pass.
