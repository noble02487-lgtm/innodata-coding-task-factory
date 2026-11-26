"""Feature tests for the Duration parameter type (click.Duration).

These tests FAIL on the base commit (the type does not exist) and PASS
with the reference implementation applied.
"""

from datetime import timedelta

import pytest

import click
from click.testing import CliRunner


@pytest.fixture()
def runner():
    return CliRunner()


def make_cli():
    @click.command()
    @click.option("--wait", type=click.Duration(), required=True)
    def cli(wait):
        click.echo(str(wait.total_seconds()))

    return cli


def test_duration_is_exported():
    assert hasattr(click, "Duration")
    assert repr(click.Duration()) == "Duration"
    assert click.Duration().name == "duration"


@pytest.mark.parametrize(
    ("raw", "seconds"),
    [
        ("45s", 45.0),
        ("90", 90.0),
        ("1.5", 1.5),
        ("2m", 120.0),
        ("1h", 3600.0),
        ("1h30m", 5400.0),
        ("1h 30m", 5400.0),
        ("2d", 172800.0),
        ("1w", 604800.0),
        ("1w2d4h", 792000.0),
        ("500ms", 0.5),
        ("1.5h", 5400.0),
        ("0s", 0.0),
        ("1H30M", 5400.0),
    ],
)
def test_duration_parses(runner, raw, seconds):
    result = runner.invoke(make_cli(), ["--wait", raw])
    assert result.exit_code == 0, result.output
    assert float(result.output.strip()) == seconds


def test_duration_returns_timedelta():
    @click.command()
    @click.argument("span", type=click.Duration())
    def cli(span):
        assert isinstance(span, timedelta)
        click.echo("ok")

    result = CliRunner().invoke(cli, ["3d12h"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "ok"


def test_duration_default_value():
    @click.command()
    @click.option("--wait", type=click.Duration(), default="10m")
    def cli(wait):
        click.echo(str(wait.total_seconds()))

    result = CliRunner().invoke(cli, [])
    assert result.exit_code == 0, result.output
    assert float(result.output.strip()) == 600.0


@pytest.mark.parametrize("raw", ["", "abc", "10x", "h30m", "1h30", "-5s", "1hh"])
def test_duration_rejects_invalid(runner, raw):
    result = runner.invoke(make_cli(), ["--wait", raw])
    assert result.exit_code != 0
    assert "not a valid duration" in result.output


def test_duration_metavar_in_help(runner):
    result = runner.invoke(make_cli(), ["--help"])
    assert result.exit_code == 0
    assert "DURATION" in result.output
