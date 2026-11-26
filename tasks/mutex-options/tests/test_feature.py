"""Feature tests for mutually exclusive options (Option(exclusive_group=...)).

These tests FAIL on the base commit (the parameter does not exist) and PASS
with the reference implementation applied.
"""

import click
from click.testing import CliRunner


def make_cli():
    @click.command()
    @click.option("--json", "fmt_json", is_flag=True, exclusive_group="format")
    @click.option("--yaml", "fmt_yaml", is_flag=True, exclusive_group="format")
    @click.option("--xml", "fmt_xml", is_flag=True, exclusive_group="format")
    @click.option("--verbose", is_flag=True)
    def cli(fmt_json, fmt_yaml, fmt_xml, verbose):
        click.echo("ran")

    return cli


def test_single_group_member_is_fine():
    result = CliRunner().invoke(make_cli(), ["--json"])
    assert result.exit_code == 0, result.output
    assert "ran" in result.output


def test_no_group_member_is_fine():
    result = CliRunner().invoke(make_cli(), ["--verbose"])
    assert result.exit_code == 0, result.output


def test_two_group_members_conflict():
    result = CliRunner().invoke(make_cli(), ["--json", "--yaml"])
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output
    assert "--json" in result.output
    assert "--yaml" in result.output


def test_three_group_members_conflict():
    result = CliRunner().invoke(make_cli(), ["--json", "--yaml", "--xml"])
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_conflict_is_usage_error_exit_code_2():
    result = CliRunner().invoke(make_cli(), ["--yaml", "--xml"])
    assert result.exit_code == 2


def test_defaults_do_not_count_as_given():
    @click.command()
    @click.option("--mode-a", default="x", exclusive_group="mode")
    @click.option("--mode-b", default="y", exclusive_group="mode")
    def cli(mode_a, mode_b):
        click.echo("ran")

    result = CliRunner().invoke(cli, [])
    assert result.exit_code == 0, result.output

    result = CliRunner().invoke(cli, ["--mode-a", "z"])
    assert result.exit_code == 0, result.output


def test_explicit_value_options_conflict():
    @click.command()
    @click.option("--host", exclusive_group="target")
    @click.option("--url", exclusive_group="target")
    def cli(host, url):
        click.echo("ran")

    result = CliRunner().invoke(cli, ["--host", "h", "--url", "u"])
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_separate_groups_do_not_interfere():
    @click.command()
    @click.option("--json", is_flag=True, exclusive_group="format")
    @click.option("--fast", is_flag=True, exclusive_group="speed")
    def cli(json, fast):
        click.echo("ran")

    result = CliRunner().invoke(cli, ["--json", "--fast"])
    assert result.exit_code == 0, result.output


def test_group_level_options_are_checked():
    @click.group()
    @click.option("--token", exclusive_group="auth")
    @click.option("--password", exclusive_group="auth")
    def cli(token, password):
        pass

    @cli.command()
    def sub():
        click.echo("sub ran")

    result = CliRunner().invoke(cli, ["--token", "t", "--password", "p", "sub"])
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_option_stores_exclusive_group():
    opt = click.Option(["--json"], exclusive_group="format")
    assert opt.exclusive_group == "format"
    opt2 = click.Option(["--plain"])
    assert opt2.exclusive_group is None
