# Add a default subcommand to Click groups

The repository at `/app` is the Click command-line library (Python), checked out at a fixed commit. Implement a "default subcommand" for groups: a fallback command that runs when the user does not name a known subcommand.

## Required API

- `click.Group` accepts a new keyword argument `default` (the name of a registered subcommand, default `None`), stored as the attribute `group.default`. Because the `click.group()` decorator passes keyword arguments through, `@click.group(default="run")` must work.

## Behavior

For a group created with `default="run"` (where `run` is one of its subcommands):

- Invoking the group with **no arguments at all** runs the default subcommand (with its own defaults) instead of printing help or failing with "Missing command."
- Invoking the group with a **first argument that is not a known subcommand name and does not start with `-`** runs the default subcommand with **all** the given arguments (so positional arguments and options of the default subcommand work: `cli mars --shout` passes `mars` and `--shout` to `run`).
- Invoking a known subcommand by name behaves exactly as before.
- Groups without a `default` behave exactly as before (missing/unknown commands are errors).
- Chained groups (`chain=True`) are not affected by the fallback.

## Example

```python
@click.group(default="run")
def cli():
    pass

@cli.command()
@click.argument("target", required=False, default="world")
def run(target):
    click.echo(f"running {target}")

@cli.command()
def status():
    click.echo("status ok")

# cli          -> running world
# cli mars     -> running mars
# cli status   -> status ok
```

All pre-existing tests in the repository's `tests/` directory must continue to pass.
