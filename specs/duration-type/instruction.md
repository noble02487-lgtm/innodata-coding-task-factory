# Add a Duration parameter type to Click

The repository at `/app` is the Click command-line library (Python), checked out at a fixed commit. Implement a new parameter type that parses human-readable duration strings.

## Required API

- A new class `Duration` in `click.types`, subclassing `ParamType`, also exported at the top level as `click.Duration`.
- Its `name` attribute is `"duration"`, `repr(Duration())` is `"Duration"`, and its help metavar is `DURATION`.

## Conversion behavior

`Duration().convert(value, param, ctx)` returns a `datetime.timedelta`:

- A `timedelta` value is returned unchanged. An `int`/`float` value means that many seconds.
- A string is one or more `<number><unit>` groups, e.g. `"45s"`, `"2m"`, `"1h30m"`, `"1h 30m"`, `"2d"`, `"1w"`, `"1w2d4h"`, `"500ms"`, `"1.5h"`.
  - Units (case-insensitive): `w` = weeks, `d` = days, `h` = hours, `m` = minutes, `s` = seconds, `ms` = milliseconds.
  - Numbers may be decimal (`"1.5h"`). Groups may be separated by whitespace.
- A bare number string with no unit (`"90"`, `"1.5"`) means seconds.
- Anything else — empty string, unknown units (`"10x"`), missing numbers (`"h30m"`), trailing numbers without a unit (`"1h30"`), negative durations (`"-5s"`) — must fail conversion through the normal `ParamType.fail` mechanism with a message containing `is not a valid duration`, so the CLI reports a usage error (exit code 2).

## Example

```python
@click.command()
@click.option("--wait", type=click.Duration(), required=True)
def cli(wait):
    click.echo(str(wait.total_seconds()))

# --wait 1h30m  ->  5400.0
```

All pre-existing tests in the repository's `tests/` directory must continue to pass.
