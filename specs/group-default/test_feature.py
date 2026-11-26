"""Feature tests for a Group default subcommand (Group(default=...)).

These tests FAIL on the base commit (Group has no default subcommand)
and PASS with the reference implementation applied.
"""

import click
from click.testing import CliRunner


def make_cli():
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

    return cli


def test_explicit_command_still_works():
    result = CliRunner().invoke(make_cli(), ["status"])
    assert result.exit_code == 0, result.output
    assert "status ok" in result.output


def test_no_args_runs_default():
    result = CliRunner().invoke(make_cli(), [])
    assert result.exit_code == 0, result.output
    assert "running world" in result.output


def test_unknown_first_arg_goes_to_default():
    result = CliRunner().invoke(make_cli(), ["mars"])
    assert result.exit_code == 0, result.output
    assert "running mars" in result.output


def test_explicit_default_command_works():
    result = CliRunner().invoke(make_cli(), ["run", "venus"])
    assert result.exit_code == 0, result.output
    assert "running venus" in result.output


def test_default_attribute_stored():
    grp = click.Group("cli", default="run")
    assert grp.default == "run"
    grp2 = click.Group("cli")
    assert grp2.default is None


def test_default_receives_its_own_options_after_positional():
    @click.group(default="run")
    def cli():
        pass

    @cli.command()
    @click.argument("target")
    @click.option("--shout", is_flag=True)
    def run(target, shout):
        msg = f"running {target}"
        click.echo(msg.upper() if shout else msg)

    @cli.command()
    def status():
        click.echo("status ok")

    result = CliRunner().invoke(cli, ["mars", "--shout"])
    assert result.exit_code == 0, result.output
    assert "RUNNING MARS" in result.output
