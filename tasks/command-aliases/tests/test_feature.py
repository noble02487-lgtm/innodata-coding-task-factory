"""Feature tests for subcommand aliases (@group.command(aliases=[...])).

These tests FAIL on the base commit (commands have no aliases) and PASS
with the reference implementation applied.
"""

import click
from click.testing import CliRunner


def make_cli():
    @click.group()
    def cli():
        pass

    @cli.command(aliases=["ls", "dir"])
    def list_items():
        click.echo("listing")

    @cli.command()
    def status():
        click.echo("status ok")

    return cli


def test_canonical_name_still_works():
    result = CliRunner().invoke(make_cli(), ["list-items"])
    assert result.exit_code == 0, result.output
    assert "listing" in result.output


def test_alias_invokes_command():
    for alias in ("ls", "dir"):
        result = CliRunner().invoke(make_cli(), [alias])
        assert result.exit_code == 0, (alias, result.output)
        assert "listing" in result.output


def test_alias_with_arguments():
    @click.group()
    def cli():
        pass

    @cli.command(aliases=["rm"])
    @click.argument("name")
    def remove(name):
        click.echo(f"removed {name}")

    result = CliRunner().invoke(cli, ["rm", "thing"])
    assert result.exit_code == 0, result.output
    assert "removed thing" in result.output


def test_alias_help_works():
    result = CliRunner().invoke(make_cli(), ["ls", "--help"])
    assert result.exit_code == 0, result.output


def test_command_help_lists_aliases():
    result = CliRunner().invoke(make_cli(), ["list-items", "--help"])
    assert result.exit_code == 0, result.output
    assert "Aliases" in result.output
    assert "ls" in result.output
    assert "dir" in result.output


def test_group_help_lists_canonical_only():
    result = CliRunner().invoke(make_cli(), ["--help"])
    assert result.exit_code == 0, result.output
    assert "list-items" in result.output
    # Aliases are not listed as separate commands in the group help.
    lines = result.output.splitlines()
    command_lines = [ln for ln in lines if ln.strip().startswith(("ls", "dir"))]
    assert command_lines == []


def test_unknown_command_still_fails():
    result = CliRunner().invoke(make_cli(), ["lst"])
    assert result.exit_code != 0


def test_command_object_stores_aliases():
    cmd = click.Command("list-items", aliases=["ls", "dir"])
    assert cmd.aliases == ["ls", "dir"]
    plain = click.Command("status")
    assert plain.aliases == []


def test_alias_does_not_shadow_real_command():
    @click.group()
    def cli():
        pass

    @cli.command(aliases=["status"])
    def other():
        click.echo("other")

    @cli.command()
    def status():
        click.echo("real status")

    result = CliRunner().invoke(cli, ["status"])
    assert result.exit_code == 0, result.output
    assert "real status" in result.output
