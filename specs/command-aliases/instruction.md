# Add subcommand aliases to Click groups

The repository at `/app` is the Click command-line library (Python), checked out at a fixed commit. Implement alternate names ("aliases") for subcommands of a group.

## Required API

- `click.Command` accepts a new keyword argument `aliases` (a sequence of strings, default empty), stored as the attribute `command.aliases` (a list; empty when not given). Because group/command decorators pass keyword arguments through to the command class, `@cli.command(aliases=["ls"])` must work.

## Behavior

- Invoking a group with an alias instead of the canonical name runs that command, including its arguments and options: `cli ls` behaves like `cli list-items` if `list-items` declared `aliases=["ls"]`.
- Asking for help through an alias (`cli ls --help`) works.
- The command's own help output (`cli list-items --help`) shows its aliases in a line containing `Aliases:` followed by the alias names.
- The group's help lists only canonical command names — aliases are not shown as separate commands.
- If an alias happens to equal the canonical name of another command in the same group, the real command wins: invoking that name runs the real command, not the alias target.
- Unknown names still produce the usual "No such command" error.

## Example

```python
@click.group()
def cli():
    pass

@cli.command(aliases=["ls", "dir"])
def list_items():
    click.echo("listing")

# cli list-items / cli ls / cli dir  ->  all print "listing"
```

All pre-existing tests in the repository's `tests/` directory must continue to pass.
