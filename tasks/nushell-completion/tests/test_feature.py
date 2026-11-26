"""Feature tests for Nushell completion support (NushellComplete).

These tests FAIL on the base commit (nushell is not a registered shell)
and PASS with the reference implementation applied.
"""

import click
import click.shell_completion
from click.shell_completion import get_completion_class
from click.testing import CliRunner

NushellComplete = getattr(click.shell_completion, "NushellComplete", None)


def make_cli():
    @click.group()
    def cli():
        pass

    @cli.command()
    def alpha():
        """First command."""

    @cli.command()
    def beta():
        """Second command."""

    return cli


def test_nushell_class_is_registered():
    assert NushellComplete is not None
    assert get_completion_class("nushell") is NushellComplete


def test_nushell_source_script():
    result = CliRunner().invoke(
        make_cli(), env={"_CLI_COMPLETE": "nushell_source"}
    )
    assert result.exit_code == 0, result.output
    assert "nushell_complete" in result.output
    assert "nu-complete cli" in result.output
    assert 'extern "cli"' in result.output


def test_nushell_completion_output(monkeypatch):
    assert NushellComplete is not None
    cli = make_cli()
    monkeypatch.setenv("COMP_WORDS", "cli ")
    monkeypatch.setenv("COMP_CWORD", "1")
    comp = NushellComplete(cli, {}, "cli", "_CLI_COMPLETE")
    out = comp.complete()
    # Three lines per item: type, value, help ("_" when missing).
    lines = out.splitlines()
    assert lines[0] == "plain"
    assert lines[1] == "alpha"
    assert lines[2] == "First command."
    assert lines[3] == "plain"
    assert lines[4] == "beta"
    assert lines[5] == "Second command."


def test_nushell_partial_word(monkeypatch):
    assert NushellComplete is not None
    cli = make_cli()
    monkeypatch.setenv("COMP_WORDS", "cli al")
    monkeypatch.setenv("COMP_CWORD", "1")
    comp = NushellComplete(cli, {}, "cli", "_CLI_COMPLETE")
    out = comp.complete()
    assert "alpha" in out
    assert "beta" not in out


def test_nushell_end_to_end_complete_env(monkeypatch):
    cli = make_cli()
    monkeypatch.setenv("_CLI_COMPLETE", "nushell_complete")
    monkeypatch.setenv("COMP_WORDS", "cli ")
    monkeypatch.setenv("COMP_CWORD", "1")
    result = CliRunner().invoke(cli, [])
    assert result.exit_code == 0, result.output
    assert "alpha" in result.output
    assert "beta" in result.output
